from widget.table_view_template import TableViewTemplate


class PnlCoinTableView(TableViewTemplate):
    def __init__(self, parent=None):
        super(PnlCoinTableView, self).__init__(parent=parent)
        self.action_group['sum']['column_list'] = ['총 매수금액', '총 매도금액', '실현손익']
