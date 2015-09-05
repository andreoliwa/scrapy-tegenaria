"""Enhancements to the FlaskTable plugin."""
from babel.dates import format_date, format_datetime
from flask_table import Col as OriginalCol
from flask_table import Table as OriginalTable


class Table(OriginalTable):

    """An enhanced table based on the original from FlaskTable.

    This table injects a ``row`` attribute in every column, so they can read other data from the same record.
    """

    def sort_url(self, col_id, reverse=False):
        """Create a URL for sorting. Must be replaced in inherited classes."""
        raise NotImplementedError

    def tr(self, item):
        """Inject a row attribute in every column, then call the parent method."""
        for field, column in self._cols.items():  # pylint: disable=no-member
            column.field = field
            column.row = item
        return super(Table, self).tr(item)


class Col(OriginalCol):

    """An enhanced column based on the original from FlaskTable.

    This column has a ``row`` attribute to read other data from the same record.
    """

    def __init__(self, *args, cell=None, allow_sort=False, **kwargs):
        """Create a column.

        :param args: Positional arguments.
        :param cell: A function that receives 3 arguments: row, col and value.
            This can be a lambda to be used in the declaration of the column.
            This function replaces the ``td_format`` function.
        :type cell: lambda
        :param allow_sort: Flag to allow sorting in the column header.
        :param kwargs: Key value arguments.
        """
        self.field = None
        self.row = None
        if callable(cell):
            self.td_format = self._replace_td_format(cell)
        super(Col, self).__init__(*args, allow_sort=allow_sort, **kwargs)

    @property
    def index(self):
        """Return the numeric index of the column in the table."""
        return self._counter

    def _replace_td_format(self, cell_lambda):
        """Replace the original td_format function by a lambda provided at column creation.

        :param cell_lambda: Function received as argument in __init__().
        :return: A function with the original td_format signature.
        """
        def original_td_format(content):
            """Call the lambda function passing row, col and current value of the cell."""
            return cell_lambda(self.row, self, content)
        return original_td_format


class UrlCol(Col):  # pylint: disable=no-init

    """A column that displays a URL."""

    def td_format(self, content):  # pylint: disable=method-hidden
        """Format the content as a URL targeting a blank page."""
        return '<a href="{url}" target="_blank">{title}</a>'.format(url=self.row.url, title=self.row.title)


class DateCol(Col):

    """Format the content as a date, unless it is None, in which case, output empty."""

    def __init__(self, name, date_format='short', **kwargs):
        """Create a date column."""
        Col.__init__(self, name, **kwargs)
        self.date_format = date_format

    def td_format(self, content):  # pylint: disable=method-hidden
        """Format a date column."""
        if content:
            return format_date(content, self.date_format)
        else:
            return ''


class DatetimeCol(Col):

    """Format the content as a datetime, unless it is None, in which case, output empty."""

    def __init__(self, name, **kwargs):
        """Create a date time column."""
        Col.__init__(self, name, **kwargs)
        self.datetime_format = kwargs.get('datetime_format', 'short')

    def td_format(self, content):  # pylint: disable=method-hidden
        """Format a date time column."""
        if content:
            return format_datetime(content, self.datetime_format)
        else:
            return ''
