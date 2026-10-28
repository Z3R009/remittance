"""Pure-Python builders for the PACSVAL / PER OO / JEV prints.

Nothing in here imports Odoo, so it can be unit-tested on its own.  Each
builder takes ``rows`` - a list of plain dicts, one per take.home.pay record
(see ``THP_FIELDS`` plus the meta keys ``name``, ``item_no``, ``sg``,
``step`` and ``program``) - and returns the values the QWeb templates loop over.
"""
import calendar
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

# ---------------------------------------------------------------------------
# PER OO configuration
# ---------------------------------------------------------------------------
GSIS_EMPLOYER_RATE = 0.12  # "GSIS RLIP (12%)" column = basic salary x 12%
ECIP_SHARE = 100.0         # "ECIP" column: flat amount per employee with a salary

# (key, section title, subtotal label) - order = order printed on PER OO
OO_PROGRAMS = [
    ('gms', 'General Management & Supervision', 'GRAND TOTAL - GMS'),
    ('oo1', 'OO1 - Exports & Investment Program', 'SUB-TOTAL OO1'),
    ('oo2', 'OO2 - Industry Development Program', 'SUB-TOTAL OO2'),
    ('oo3', 'OO3 - MSME Development Program', 'SUB-TOTAL OO3'),
    ('oo4_1', 'OO4.1 - Consumer Protection Program', 'SUB-TOTAL OO4.1'),
    ('oo4_2', 'OO4.2 - Consumer Education and Advocacy Program', 'SUB-TOTAL OO4.2'),
]
UNASSIGNED = ('', 'No OO / Program assigned', 'SUB-TOTAL (UNASSIGNED)')

PER_OO_COLUMNS = ('total', 'gsis', 'ecip', 'hdmf', 'phic', 'basic', 'pera',
                  'ra', 'ta', 'first', 'second')

# ---------------------------------------------------------------------------
# JEV configuration: (label, account code, side, [take.home.pay fields])
# Salary-loan / policy-loan / premium groupings follow the JEV(1st Half) sheet.
# ---------------------------------------------------------------------------
JEV_LINES = [
    ('Salaries And Wages - REGULAR', '5-01-01-010 01', 'dr', ['basic_salary']),
    ('Personal Economic Relief Allowance', '5-01-02-010 01', 'dr', ['pera']),
    ('Representation Allowance', '5-01-02-020 00', 'dr', ['representation_allowance']),
    ('Transportation Allowance', '5-01-02-030 01', 'dr', ['transportation_allowance']),
    ('Due to BIR', '2-02-01-010 00', 'cr', ['withholding_tax']),
    ('Due to GSIS - Life and Retirement Premium', '2-02-01-020 01', 'cr', ['gsis_rlip']),
    ('Due to GSIS - Salary Loan', '2-02-01-020 03', 'cr', [
        'gsis_conso_loan', 'gsis_mpl_lite', 'gsis_mpl', 'gsis_emergency_loan',
        'gsis_computer_loan', 'gsis_educ_loan', 'gsis_solar_loan',
        'gsis_opt_life_pre', 'gsis_e_bike', 'gsis_rel', 'gsis_gfal_2']),
    ('Due to GSIS - Policy Loan', '2-02-01-020 04', 'cr',
     ['gsis_policy_loan_reg', 'gsis_policy_loan_opt']),
    ('Due to PAG IBIG - Premium', '2-02-01-030 01', 'cr', ['hdmf_cont1', 'hdmf_mp2']),
    ('Due to PAG IBIG - MPL/ Calamity Loan', '2-02-01-030 02', 'cr',
     ['hdmf_mpl', 'hdmf_calamity_loan']),
    ('Due to PAG IBIG - HL/SAF', '2-02-01-030 03', 'cr', ['hdmf_housing', 'hdmf_saf']),
    ('Due to Philhealth', '2-02-01-040 00', 'cr', ['philhealth']),
    ('Other Payables - DTI- PF Cont., PF Loan', '2-99-99-990 00', 'cr',
     ['dti_pf_cont', 'dti_pf_loan']),
    ('Other Payables - MDBF', '2-99-99-990 00', 'cr', ['mdbf']),
    ('Other Payables - DTI-EU Monthly Dues', '2-99-99-990 00', 'cr', ['dti_eu_dues']),
    ('Other Payables - DTI-EU HMO', '2-99-99-990 00', 'cr', ['dti_eu_hmo']),
    ('Other payables - LBP Loan', '2-99-99-990 00', 'cr', ['lbp_dbp']),
    # No take.home.pay field exists for postpaid handsets, so this stays blank.
    ('Other payables - POSTPAID', '2-99-99-990 00', 'cr', []),
    ('Other payables - GLOBE', '2-99-99-990 00', 'cr', ['globe']),
    ('Other payables - AMAPHIL', '2-99-99-990 00', 'cr', ['amaphil']),
    ('Other payables - WHC', '2-99-99-990 00', 'cr', ['whc']),
    # SUMMARY "OTHERS" column has no take.home.pay field either.
    ('Due from officers and Employees', '1-05-05-020-00', 'cr', []),
]

# Every take.home.pay field the builders read.
THP_FIELDS = sorted(
    {f for _l, _c, _s, fields_ in JEV_LINES for f in fields_}
    | {'basic_salary', 'pera', 'representation_allowance',
       'transportation_allowance', 'hdmf_cont1', 'philhealth',
       'total_net_1st', 'total_net_2nd'}
)


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------
def fmt(value, dash=False):
    """Format like Excel's 2-decimal display (half-up on the stored 3 dp).

    Python's own '{:.2f}' rounds 12107.525 down (binary float); Excel shows
    12,107.53, and the workbook is the reference, so round half-up here.
    """
    value = round(value or 0.0, 3)
    if dash and not value:
        return '-'
    cents = Decimal(repr(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return '{:,.2f}'.format(cents)


def month_title(payroll_month):
    """'2026-09-01' -> 'FOR THE MONTH OF SEPTEMBER 2026'."""
    d = date.fromisoformat(payroll_month)
    return 'FOR THE MONTH OF %s %d' % (d.strftime('%B').upper(), d.year)


def period_label(payroll_month):
    """'2026-09-01' -> 'SEPTEMBER 1-30, 2026'."""
    d = date.fromisoformat(payroll_month)
    last = calendar.monthrange(d.year, d.month)[1]
    return '%s 1-%d, %d' % (d.strftime('%B').upper(), last, d.year)

def name_key(name):
    """Sort key like Excel's: case-insensitive, ignoring hyphens and apostrophes."""
    return (name or '').casefold().replace('-', '').replace("'", '')


# ---------------------------------------------------------------------------
# PACSVAL
# ---------------------------------------------------------------------------
def build_pacsval(rows):
    keys = ('ra', 'ta', 'first', 'first_total', 'second', 'total')
    totals = dict.fromkeys(keys, 0.0)
    lines = []
    for no, r in enumerate(sorted(rows, key=lambda r: name_key(r['name'])), 1):
        ra = r['representation_allowance']
        ta = r['transportation_allowance']
        first, second = r['total_net_1st'], r['total_net_2nd']
        line = {
            'no': no, 'name': r['name'], 'ra': ra, 'ta': ta, 'first': first,
            'first_total': ra + ta + first, 'second': second,
            'total': ra + ta + first + second,
        }
        for k in keys:
            totals[k] += line[k]
        lines.append(line)
    return {'lines': lines, 'totals': totals}


# ---------------------------------------------------------------------------
# PER OO
# ---------------------------------------------------------------------------
def _oo_row(r):
    basic = r['basic_salary']
    line = {
        'item_no': r['item_no'], 'sg': r['sg'] or '', 'step': r['step'] or '',
        'name': r['name'],
        'gsis': basic * GSIS_EMPLOYER_RATE,
        'ecip': ECIP_SHARE if basic else 0.0,
        'hdmf': r['hdmf_cont1'],
        'phic': r['philhealth'],
        'basic': basic,
        'pera': r['pera'],
        'ra': r['representation_allowance'],
        'ta': r['transportation_allowance'],
        'first': r['total_net_1st'],
        'second': r['total_net_2nd'],
        '_sg_sort': r['sg'] or 0,
    }
    line['total'] = sum(line[k] for k in
                        ('gsis', 'ecip', 'hdmf', 'phic', 'basic', 'pera', 'ra', 'ta'))
    return line


def _sum_rows(lines):
    out = {k: sum(l[k] for l in lines) for k in PER_OO_COLUMNS}
    out['count'] = len(lines)
    return out


def _add(a, b):
    return {k: a[k] + b[k] for k in list(PER_OO_COLUMNS) + ['count']}


def build_per_oo(rows):
    known = {key for key, _t, _l in OO_PROGRAMS}
    buckets = {key: [] for key, _t, _l in OO_PROGRAMS}
    buckets[UNASSIGNED[0]] = []
    for r in rows:
        key = r['program'] if r['program'] in known else UNASSIGNED[0]
        buckets[key].append(_oo_row(r))

    groups = []
    for key, title, label in OO_PROGRAMS + [UNASSIGNED]:
        lines = sorted(buckets[key],
                       key=lambda l: (-l['_sg_sort'], l['item_no'], l['name'].casefold()))
        if not lines and key == UNASSIGNED[0]:
            continue  # only show the catch-all block when something landed in it
        groups.append({
            'key': key, 'title': title.upper(), 'label': label,
            'lines': lines, 'subtotal': _sum_rows(lines),
        })

    zero = _sum_rows([])
    oo_total = zero
    for g in groups:
        if g['key'] != 'gms':
            oo_total = _add(oo_total, g['subtotal'])
    gms = next((g['subtotal'] for g in groups if g['key'] == 'gms'), zero)
    return {'groups': groups, 'oo_total': oo_total, 'grand_total': _add(gms, oo_total)}


# ---------------------------------------------------------------------------
# JEV
# ---------------------------------------------------------------------------
def build_jev(rows):
    def total(fields_):
        return sum(r[f] for r in rows for f in fields_)

    debit_lines, credit_lines = [], []
    for label, code, side, fields_ in JEV_LINES:
        line = {'label': label, 'code': code, 'amount': total(fields_)}
        (debit_lines if side == 'dr' else credit_lines).append(line)

    sum_dr = sum(l['amount'] for l in debit_lines)
    sum_cr = sum(l['amount'] for l in credit_lines)
    payable = sum_dr - sum_cr  # "Due to officers and Employees" = net pay incl. RA/TA

    lines = (
        [dict(l, dr=l['amount'], cr=None, indent=False) for l in debit_lines]
        + [dict(l, dr=None, cr=l['amount'], indent=True) for l in credit_lines]
        + [
            {'label': 'Due to officers and Employees', 'code': '2-01-01-020 00',
             'dr': None, 'cr': payable, 'indent': True},
            {'label': 'Due to Officers and Employees', 'code': '2-01-01-020 00',
             'dr': payable, 'cr': None, 'indent': False},
            {'label': 'Cash - MDS, REGULAR', 'code': '1-01-04-040 00',
             'dr': None, 'cr': payable, 'indent': True},
        ]
    )

    # Cross-check against the take-home-pay halves the other two prints use.
    net_from_halves = (total(['total_net_1st']) + total(['total_net_2nd'])
                       + total(['representation_allowance'])
                       + total(['transportation_allowance']))
    return {
        'lines': lines,
        'total_dr': sum_dr + payable,
        'total_cr': sum_cr + payable + payable,
        'payable': payable,
        'check_diff': payable - net_from_halves,
        'check_ok': abs(payable - net_from_halves) < 0.01,
    }


# ---------------------------------------------------------------------------
# PACSVAL month-over-month Excel export
# ---------------------------------------------------------------------------
COMPARE_SECTIONS = [('main', 'REGULAR'), ('carp', 'CARP'), ('nc_tida', 'NC')]
XLSX_ACCOUNTING = '_(* #,##0.00_);_(* \\(#,##0.00\\);_(* "-"??_);_(@_)'


def build_pacsval_compare(cur_rows, prev_rows):
    result = {}
    for key, _label in COMPARE_SECTIONS:
        merged = {}
        for field, rows in (('prev', prev_rows), ('cur', cur_rows)):
            for r in rows:
                if r['section'] != key:
                    continue
                m = merged.setdefault(
                    r['emp'], {'name': r['name'], 'seq': r['seq'], 'cur': 0.0, 'prev': 0.0})
                m[field] += r['total']
                if field == 'cur':  # current month decides name and order
                    m['name'], m['seq'] = r['name'], r['seq']
        if not merged:
            continue
        if key == 'main':
            order = lambda m: name_key(m['name'])
        else:
            order = lambda m: (m['seq'], name_key(m['name']))
        result[key] = [
            {'no': no, 'name': m['name'], 'cur': m['cur'], 'prev': m['prev']}
            for no, m in enumerate(sorted(merged.values(), key=order), 1)
        ]
    return result


def build_compare_xlsx(sections, cur_label, prev_label):
    import io
    import xlsxwriter
    from xlsxwriter.utility import xl_rowcol_to_cell as cell

    stream = io.BytesIO()
    wb = xlsxwriter.Workbook(stream, {'in_memory': True})
    ws = wb.add_worksheet('PACSVAL')
    bold = wb.add_format({'bold': True})
    head = wb.add_format({'bold': True, 'align': 'center'})
    money = wb.add_format({'num_format': XLSX_ACCOUNTING})
    total = wb.add_format({'bold': True, 'num_format': XLSX_ACCOUNTING, 'bottom': 6})
    labels = dict(COMPARE_SECTIONS)

    def block(row0, col0, key, lines):
        ws.write_string(row0, col0 + 1, labels[key], bold)
        ws.write_string(row0 + 1, col0 + 2, cur_label, head)
        ws.write_string(row0 + 1, col0 + 3, prev_label, head)
        ws.write_string(row0 + 1, col0 + 4, 'VARIANCE', head)
        r = row0 + 2
        for ln in lines:
            ws.write_number(r, col0, ln['no'])
            ws.write_string(r, col0 + 1, ln['name'])
            ws.write_number(r, col0 + 2, round(ln['cur'], 6), money)
            ws.write_number(r, col0 + 3, round(ln['prev'], 6), money)
            ws.write_formula(r, col0 + 4,
                             '=%s-%s' % (cell(r, col0 + 2), cell(r, col0 + 3)), money,
                             round(ln['cur'] - ln['prev'], 6))
            r += 1
        first, last, trow = row0 + 2, r - 1, r + 1  # one blank row before the total
        sums = {2: sum(l['cur'] for l in lines), 3: sum(l['prev'] for l in lines)}
        sums[4] = sums[2] - sums[3]
        for off, value in sums.items():
            ws.write_formula(trow, col0 + off,
                             '=SUM(%s:%s)' % (cell(first, col0 + off), cell(last, col0 + off)),
                             total, round(value, 6))
        return trow

    right_row = 0
    for key, _label in COMPARE_SECTIONS:
        if key not in sections:
            continue
        if key == 'main':
            block(0, 0, key, sections[key])
        else:
            right_row = block(right_row, 8, key, sections[key]) + 2

    ws.set_column(0, 0, 5)
    ws.set_column(1, 1, 32)
    ws.set_column(2, 4, 18)
    ws.set_column(8, 8, 5)
    ws.set_column(9, 9, 32)
    ws.set_column(10, 12, 18)
    wb.close()
    return stream.getvalue()