from odoo import api, fields, models


class PayrollSummaryData(models.AbstractModel):
    _name = "report.remittance.report_payroll_summary"
    _description = "Payroll Summary Report Data"

    # (field on take.home.pay, field on employee.refund or None,
    #  field on government.share, field on remittance.amount)
    CATEGORY_MAP = {
        'page1': [
            ('PHIC', 'philhealth', None, 'gs_philhealth', 'rm_philhealth'),
            ('DTI-PF Cont', 'dti_pf_cont', None, 'gs_dti_pf_cont', 'rm_dti_pf_cont'),
            ('DTI-PF Loan', 'dti_pf_loan', 'refund_dti_pf_loan', 'gs_dti_pf_loan', 'rm_dti_pf_loan'),
            ('MDBF', 'mdbf', None, 'gs_mdbf', 'rm_mdbf'),
            ('DTI-EU Dues', 'dti_eu_dues', None, 'gs_dti_eu_dues', 'rm_dti_eu_dues'),
            ('DTI-EU HMO', 'dti_eu_hmo', None, 'gs_dti_eu_hmo', 'rm_dti_eu_hmo'),
            ('LBP Salary Loan', 'lbp_dbp', 'refund_lbp_dbp', 'gs_lbp_dbp', 'rm_lbp_dbp'),
            ('GLOBE', 'globe', 'refund_globe', 'gs_globe', 'rm_globe'),
            ('AMAPHIL', 'amaphil', None, 'gs_amaphil', 'rm_amaphil'),
            ('WHC', 'whc', None, 'gs_whc', 'rm_whc'),
        ],
        'page2': [
            ('SIC (RLIP)', 'gsis_rlip', None, 'gs_gsis_rlip', 'rm_gsis_rlip'),
            ('Conso Loan', 'gsis_conso_loan', None, 'gs_gsis_conso_loan', 'rm_gsis_conso_loan'),
            ('MPL LITE', 'gsis_mpl_lite', 'refund_mpl_lite', 'gs_gsis_mpl_lite', 'rm_gsis_mpl_lite'),
            ('MPL', 'gsis_mpl', 'refund_mpl', 'gs_gsis_mpl', 'rm_gsis_mpl'),
            ('E/L', 'gsis_emergency_loan', 'refund_emergency_loan', 'gs_gsis_emergency_loan', 'rm_gsis_emergency_loan'),
            ('CMPL', 'gsis_computer_loan', None, 'gs_gsis_computer_loan', 'rm_gsis_computer_loan'),
            ('EDU_ASST', 'gsis_educ_loan', 'refund_educ_loan', 'gs_gsis_educ_loan', 'rm_gsis_educ_loan'),
            ('PL REG', 'gsis_policy_loan_reg', 'refund_policy_loan_reg', 'gs_gsis_policy_loan_reg', 'rm_gsis_policy_loan_reg'),
            ('PL OPT', 'gsis_policy_loan_opt', None, 'gs_gsis_policy_loan_opt', 'rm_gsis_policy_loan_opt'),
            ('OPT_LIFE', 'gsis_opt_life_pre', None, 'gs_gsis_opt_life_pre', 'rm_gsis_opt_life_pre'),
            ('R.E.L.', 'gsis_rel', 'refund_rel', 'gs_gsis_rel', 'rm_gsis_rel'),
            ('GFAL II', 'gsis_gfal_2', 'refund_gfal_2', 'gs_gsis_gfal_2', 'rm_gsis_gfal_2'),
        ],
        'page3': [
            ('Cont. I', 'hdmf_cont1', None, 'gs_hdmf_cont1', 'rm_hdmf_cont1'),
            ('Cont. II', 'hdmf_mp2', 'refund_hdmf_mp2', 'gs_hdmf_mp2', 'rm_hdmf_mp2'),
            ('MPL', 'hdmf_mpl', 'refund_hdmf_mpl', 'gs_hdmf_mpl', 'rm_hdmf_mpl'),
            ('Calamity', 'hdmf_calamity_loan', 'refund_hdmf_calamity', 'gs_hdmf_calamity_loan', 'rm_hdmf_calamity_loan'),
            ('Housing', 'hdmf_housing', 'refund_hdmf_housing', 'gs_hdmf_housing', 'rm_hdmf_housing'),
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
        remittance_amt = self.env['remittance.amount'].search([
            ('payroll_month', '=', payroll_month),
        ], limit=1)
        adjustments = self.env['payroll.summary.adjustment'].search([
            ('payroll_month', '=', payroll_month),
        ])

        # Bucket records by their department's summary section, keeping each
        # individual department separate within its section (main, nc_tida, carp)
        buckets = {'main': {}, 'nc_tida': {}, 'carp': {}}
        for rec in thp_records:
            section = rec.department_id.summary_section or 'main'
            key = rec.department_id.id or 0
            if key not in buckets[section]:
                buckets[section][key] = {
                    'name': rec.department_id.name if rec.department_id else 'No Department',
                    'sequence': rec.department_id.summary_sequence or 10,
                    'records': self.env['take.home.pay'],
                }
            buckets[section][key]['records'] |= rec

        def dept_sort_key(entry):
            return (entry.get('sequence', 10), entry['name'])

        main_offices = sorted(buckets['main'].values(), key=dept_sort_key)
        nc_offices = sorted(buckets['nc_tida'].values(), key=dept_sort_key)
        carp_offices = sorted(buckets['carp'].values(), key=dept_sort_key)

        def totals_for(recs, categories):
            return {
                'basic_salary': sum(recs.mapped('basic_salary')),
                'pera': sum(recs.mapped('pera')),
                'values': [sum(recs.mapped(f)) for (_, f, _, _, _) in categories],
            }

        def adjustment_totals(adj, categories):
            by_key = {}
            for line in adj.line_ids:
                by_key[line.category_key] = by_key.get(line.category_key, 0.0) + line.amount
            return {
                'name': adj.name,
                'basic_salary': by_key.get('basic_salary', 0.0),
                'pera': by_key.get('pera', 0.0),
                'values': [by_key.get(f, 0.0) for (_, f, _, _, _) in categories],
            }

        pages = {}
        for page_key, categories in self.CATEGORY_MAP.items():
            office_rows = [
                dict(totals_for(o['records'], categories), name=o['name'])
                for o in main_offices
            ]
            nc_dept_rows = [
                dict(totals_for(o['records'], categories), name=o['name'])
                for o in nc_offices
            ]
            carp_dept_rows = [
                dict(totals_for(o['records'], categories), name=o['name'])
                for o in carp_offices
            ]

            total_main = totals_for(
                self.env['take.home.pay'].union(*[o['records'] for o in main_offices])
                if main_offices else self.env['take.home.pay'],
                categories,
            )
            nc_row = totals_for(
                self.env['take.home.pay'].union(*[o['records'] for o in nc_offices])
                if nc_offices else self.env['take.home.pay'],
                categories,
            )
            carp_row = totals_for(
                self.env['take.home.pay'].union(*[o['records'] for o in carp_offices])
                if carp_offices else self.env['take.home.pay'],
                categories,
            )
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
                for (_, _, rf, _, _) in categories
            ]
            gov_row = [
                (getattr(gov_share, gs, 0.0) if gov_share else 0.0)
                for (_, _, _, gs, _) in categories
            ]
            remittance_row = [
                (getattr(remittance_amt, rm, 0.0) if remittance_amt else 0.0)
                for (_, _, _, _, rm) in categories
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
                'nc_dept_rows': nc_dept_rows,
                'carp_row': carp_row,
                'carp_dept_rows': carp_dept_rows,
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