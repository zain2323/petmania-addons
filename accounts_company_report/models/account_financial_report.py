# -*- coding: utf-8 -*-
from odoo import fields, models, tools, api, _

class AccountFinancialReportLine(models.Model):
    _inherit = "account.financial.html.report.line"

    def _compute_amls_results(self, options_list, calling_financial_report, sign=1, operator=None):
        self.ensure_one()
        params = []
        queries = []

        AccountFinancialReportHtml = self.financial_report_id
        horizontal_groupby_list = AccountFinancialReportHtml._get_options_groupby_fields(options_list[0])
        groupby_list = [self.groupby] + horizontal_groupby_list
        groupby_clause = ','.join('account_move_line.%s' % gb for gb in groupby_list)
        groupby_field = self.env['account.move.line']._fields[self.groupby]

        ct_query = self.env['res.currency']._get_query_currency_table(options_list[0])
        parent_financial_report = self._get_financial_report()

        for i, options in enumerate(options_list):
            new_options = self._get_options_financial_line(options, calling_financial_report, parent_financial_report)
            line_domain = self._get_domain(new_options, parent_financial_report)

            tables, where_clause, where_params = AccountFinancialReportHtml._query_get(new_options, domain=line_domain)

            queries.append('''
                SELECT
                    ''' + (groupby_clause and '%s,' % groupby_clause) + '''
                    %s AS period_index,
                    COALESCE(SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)), 0.0) AS balance
                FROM ''' + tables + '''
                JOIN ''' + ct_query + ''' ON currency_table.company_id = account_move_line.company_id
                WHERE ''' + where_clause + '''
                ''' + (groupby_clause and 'GROUP BY %s' % groupby_clause) + '''
            ''')
            params += [i] + where_params

        # Fetch the results.

        results = {}

        total_balance = 0.0
        self._cr.execute(' UNION ALL '.join(queries), params)
        for res in self._cr.dictfetchall():
            balance = res['balance']
            total_balance += balance

            # Build the key.
            key = [res['period_index']]
            for gb in horizontal_groupby_list:
                key.append(res[gb])
            key = tuple(key)

            add_line = (
                not operator
                or operator in ('sum', 'sum_if_pos', 'sum_if_neg')
                or (operator == 'sum_if_pos_groupby' and balance >= 0.0)
                or (operator == 'sum_if_neg_groupby' and balance < 0.0)
            )

            if add_line:
                results.setdefault(res[self.groupby], {})
                results[res[self.groupby]][key] = sign * balance

        add_line = (
            not operator
            or operator in ('sum', 'sum_if_pos_groupby', 'sum_if_neg_groupby')
            or (operator == 'sum_if_pos' and total_balance >= 0.0)
            or (operator == 'sum_if_neg' and total_balance < 0.0)
        )
        if not add_line:
            results = {}

        # Sort the lines according to the vertical groupby and compute their display name.
        if groupby_field.relational:
            # Preserve the table order by using search instead of browse.
            sorted_records = self.env[groupby_field.comodel_name].search([('id', 'in', tuple(results.keys()))])
            sorted_values = sorted_records.name_get()
        else:
            # Sort the keys in a lexicographic order.
            sorted_values = [(v, v) for v in sorted(list(results.keys()))]
        account_obj = self.env['account.account'].sudo().search([])
        def get_company_name(account_id):
            acc = account_obj.filtered(lambda x: x.id == account_id)
            return acc.company_id.name if acc.company_id else ""

        sorted_values = [(i[0], i[1] +" [" + get_company_name(i[0]) + "]" ) for i in sorted_values]
        return [(groupby_key, display_name, results[groupby_key]) for groupby_key, display_name in sorted_values]
