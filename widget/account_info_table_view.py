from widget.table_view_template import TableViewTemplate


class AccountInfoTableView(TableViewTemplate):
    def __init__(self, parent=None):
        super(AccountInfoTableView, self).__init__(parent=parent)
        self.action_group['sum']['column_list'] = ['매수금액', '평가금액', '평가손익']
