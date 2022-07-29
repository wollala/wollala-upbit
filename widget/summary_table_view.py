from widget.table_view_template import TableViewTemplate


class SummaryTableView(TableViewTemplate):
    def __init__(self, parent=None):
        super(SummaryTableView, self).__init__(parent=parent)
        self.menu.removeAction(self.action_group['sum']['action'])
