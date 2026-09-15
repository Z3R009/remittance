from odoo import api, fields, models


class PayrollSummaryData(models.AbstractModel):
    _name = "report.remittance.report_payroll_summary"
    _description = "Payroll Summary Report Data"

    # (field on take.home.pay, field on employee.refund or None, field on government.share)
    CATEGORY_MAP = {
        'page1': [
            ('PHIC', 'philhealth', None, 'gs_philhealth'),
            ('DTI-PF Cont', 'dti_pf_cont', None, 'gs_dti_pf_cont'),
            ('DTI-PF Loan', 'dti_pf_loan', 'refund_dti_pf_loan', 'gs_dti_pf_loan'),
            ('MDBF', 'mdbf', None, 'gs_mdbf'),
            ('DTI-EU Dues', 'dti_eu_dues', None, 'gs_dti_eu_dues'),
            ('DTI-EU HMO', 'dti_eu_hmo', None, 'gs_dti_eu_hmo'),
            ('LBP Salary Loan', 'lbp_dbp', 'refund_lbp_dbp', 'gs_lbp_dbp'),
            ('GLOBE', 'globe', 'refund_globe', 'gs_globe'),
            ('AMAPHIL', 'amaphil', None, 'gs_amaphil'),
            ('WHC', 'whc', None, 'gs_whc'),
        ],
        'page2': [
            ('SIC (RLIP)', 'gsis_rlip', None, 'gs_gsis_rlip'),
            ('Conso Loan', 'gsis_conso_loan', None, 'gs_gsis_conso_loan'),
            ('MPL LITE', 'gsis_mpl_lite', 'refund_mpl_lite', 'gs_gsis_mpl_lite'),
            ('MPL', 'gsis_mpl', 'refund_mpl', 'gs_gsis_mpl'),
            ('E/L', 'gsis_emergency_loan', 'refund_emergency_loan', 'gs_gsis_emergency_loan'),
            ('CMPL', 'gsis_computer_loan', None, 'gs_gsis_computer_loan'),
            ('EDU_ASST', 'gsis_educ_loan', 'refund_educ_loan', 'gs_gsis_educ_loan'),
            ('PL REG', 'gsis_policy_loan_reg', 'refund_policy_loan_reg', 'gs_gsis_policy_loan_reg'),
            ('PL OPT', 'gsis_policy_loan_opt', None, 'gs_gsis_policy_loan_opt'),
            ('OPT_LIFE', 'gsis_opt_life_pre', None, 'gs_gsis_opt_life_pre'),
            ('R.E.L.', 'gsis_rel', 'refund_rel', 'gs_gsis_rel'),
            ('GFAL II', 'gsis_gfal_2', 'refund_gfal_2', 'gs_gsis_gfal_2'),
        ],
        'page3': [
            ('Cont. I', 'hdmf_cont1', None, 'gs_hdmf_cont1'),
            ('Cont. II', 'hdmf_mp2', 'refund_hdmf_mp2', 'gs_hdmf_mp2'),
            ('MPL', 'hdmf_mpl', 'refund_hdmf_mpl', 'gs_hdmf_mpl'),
            ('Calamity', 'hdmf_calamity_loan', 'refund_hdmf_calamity', 'gs_hdmf_calamity_loan'),
            ('Housing', 'hdmf_housing', 'refund_hdmf_housing', 'gs_hdmf_housing'),
        ],
    }

    @api.model
    def _get_report_values(self, docids, data=None):
        payroll_month = data.get('payroll_month') if data else None

        thp_records = self.env['take.home.pay'].search([
            ('payroll_month', '=', payroll_month),
        ])
        refund_records = self.env['employee.refund'].search([
            ('payroll_month', '=', payroll_month),
        ])
        gov_share = self.env['government.share'].search([
            ('payroll_month', '=', payroll_month),
        ], limit=1)
        adjustments = self.env['payroll.summary.adjustment'].search([
            ('payroll_month', '=', payroll_month),
        ])

        # Bucket records by their department's summary section
        buckets = {'main': {}, 'nc_tida': self.env['take.home.pay'],
                   'carp': self.env['take.home.pay']}
        for rec in thp_records:
            section = rec.department_id.summary_section or 'main'
            if section == 'main':
                key = rec.department_id.id or 0
                if key not in buckets['main']:
                    buckets['main'][key] = {
                        'name': rec.department_id.name if rec.department_id else 'No Department',
                        'records': self.env['take.home.pay'],
                    }
                buckets['main'][key]['records'] |= rec
            else:
                buckets[section] |= rec

        main_offices = sorted(buckets['main'].values(), key=lambda d: d['name'])

        def totals_for(recs, categories):
            return {
                'basic_salary': sum(recs.mapped('basic_salary')),
                'pera': sum(recs.mapped('pera')),
                'values': [sum(recs.mapped(f)) for (_, f, _, _) in categories],
            }

        def adjustment_totals(adj, categories):
            by_key = {}
            for line in adj.line_ids:
                by_key[line.category_key] = by_key.get(line.category_key, 0.0) + line.amount
            return {
                'name': adj.name,
                'basic_salary': by_key.get('basic_salary', 0.0),
                'pera': by_key.get('pera', 0.0),
                'values': [by_key.get(f, 0.0) for (_, f, _, _) in categories],
            }

        pages = {}
        for page_key, categories in self.CATEGORY_MAP.items():
            office_rows = [
                dict(totals_for(o['records'], categories), name=o['name'])
                for o in main_offices
            ]

            total_main = totals_for(
                self.env['take.home.pay'].union(*[o['records'] for o in main_offices])
                if main_offices else self.env['take.home.pay'],
                categories,
            )
            nc_row = totals_for(buckets['nc_tida'], categories)
            carp_row = totals_for(buckets['carp'], categories)
            adj_rows = [adjustment_totals(a, categories) for a in adjustments]

            grand_total = {
                'basic_salary': (total_main['basic_salary'] + nc_row['basic_salary']
                                 + carp_row['basic_salary']
                                 + sum(r['basic_salary'] for r in adj_rows)),
                'pera': (total_main['pera'] + nc_row['pera'] + carp_row['pera']
                         + sum(r['pera'] for r in adj_rows)),
                'values': [
                    total_main['values'][i] + nc_row['values'][i] + carp_row['values'][i]
                    + sum(r['values'][i] for r in adj_rows)
                    for i in range(len(categories))
                ],
            }

            refund_row = [
                sum(refund_records.mapped(rf)) if rf else 0.0
                for (_, _, rf, _) in categories
            ]
            gov_row = [
                (getattr(gov_share, gs, 0.0) if gov_share else 0.0)
                for (_, _, _, gs) in categories
            ]
            remittance_row = [
                grand_total['values'][i] - refund_row[i] for i in range(len(categories))
            ]
            difference_row = [
                grand_total['values'][i] - refund_row[i] - remittance_row[i]
                for i in range(len(categories))
            ]

            pages[page_key] = {
                'headers': [c[0] for c in categories],
                'rows': office_rows,
                'total_main': total_main,
                'nc_row': nc_row,
                'carp_row': carp_row,
                'adj_rows': adj_rows,
                'grand_total': grand_total,
                'refund': refund_row,
                'remittance': remittance_row,
                'gov_share': gov_row,
                'difference': difference_row,
            }

        return {
            'doc_ids': docids,
            'doc_model': 'payroll.summary.wizard',
            'docs': self.env['payroll.summary.wizard'].browse(docids),
            'payroll_month': payroll_month,
            'month_label': fields.Date.from_string(payroll_month).strftime('%B %Y').upper() if payroll_month else '',
            'pages': pages,
        }