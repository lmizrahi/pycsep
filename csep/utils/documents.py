import os
import nbformat
from csep.utils.time import epoch_time_to_utc_datetime

class ResultsNotebook:

    def __init__(self, outname='results.ipynb'):
        self.nb = nbformat.v4.new_notebook()
        self.outname = outname
        self.nb['cells'] = []
        self.toc = []
        self.has_introduction = False

    def add_introduction(self, adict={}):
        # generate document header
        first = f"# CSEP Testing Results: {adict['simulation_name']}  \n" \
                f"**Forecast Name:** {adict['forecast_name']}  \n" \
                f"**Simulation Start Time:** {adict['origin_time']}  \n" \
                f"**Evaluation Time:** {adict['evaluation_time']}  \n" \
                f"**Catalog Source:** {adict['catalog_source']}  \n" \
                f"**Number Simulations:** {adict['num_simulations']}"

        # used to determine to place TOC at beginning of document or after introduction.
        self.has_introduction = True
        self.nb['cells'].append(nbformat.v4.new_markdown_cell(first))


    def add_result_figure(self, title, level, relative_filepaths):
        """

        Args:
            title: name of the figure
            level (int): value 1-6 depending on the heading
            relative_filepaths (str or List[Tuple[str]]): list of paths in order to make table

        Returns:

        """

        # convert str into a proper list, where each potential row is an iter not str
        def build_header(row):
            top = "|"
            bottom = "|"
            for _ in row:
                top +=  " |"
                bottom += " --- |"
            return top + '\n' + bottom

        def add_to_row(row):
            if len(row) == 1:
                return f"![]({row[0]})"
            string = '| '
            for item in row:
                string = string + f' ![]({item}) |'
            return string

        figures = []
        if isinstance(relative_filepaths, str):
            figures.append([relative_filepaths])
        else:
            figures = relative_filepaths

        level_string = f"{level*'#'}"
        result_cell = []
        locator = title.lower().replace(" ", "_")
        result_cell.append(f'{level_string} {title}  <a name="{locator}"></a>\n')

        for i, row in enumerate(figures):
            if i == 0:
                result_cell.append(build_header(row))
            result_cell.append(add_to_row(row))

        self.nb['cells'].append(nbformat.v4.new_markdown_cell('\n'.join(result_cell)))

        # generate metadata for TOC
        self.toc.append((title, level, locator))

    def add_sub_heading(self, title, level, text):
        # multipying char simply repeats it
        if isinstance(text, str):
            text = [text]
        cell = []
        level_string = f"{level*'#'}"
        locator = title.lower().replace(" ", "_")
        sub_heading = f'{level_string} {title} <a name="{locator}"></a>'
        cell.append(sub_heading)
        try:
            for item in list(text):
                cell.append(item)
        except:
            raise RuntimeWarning("Unable to add results document subheading, text must be iterable.")
        self.nb['cells'].append(nbformat.v4.new_markdown_cell('\n'.join(cell)))

        # generate metadata for TOC
        self.toc.append((title, level, locator))

    def _generate_table_of_contents(self):
        """ generates table of contents based on contents of document. """
        toc = []
        toc.append("# Table of Contents")
        # allows for 6 levels of subheadings
        inc = [0] * 6
        for title, level, locator in self.toc:
            space = '   ' * (level-1)
            toc.append(f"{space}1. [{title}](#{locator})")

        insert_loc = 1 if self.has_introduction else 0

        self.nb['cells'].insert(insert_loc, nbformat.v4.new_markdown_cell('\n'.join(toc)))


    @staticmethod
    def get_table(data, use_header=True):
        """
        Generates table from HTML and styles using bootstrap class
        Args:
           data List[Tuple[str]]: should be (nrows, ncols) in size. all rows should be the
                         same sizes

        Returns:
            table (str): this can be added to subheading or other cell if desired.

        """
        table = []
        table.append('<div class="table table-striped">')
        table.append(f'<table>')
        def make_header(row):
            header = []
            header.append('<tr>')
            for item in row:
                header.append(f'<th>{item}</th>')
            header.append('</tr>')
            return '\n'.join(header)

        def add_row(row):
            table_row = []
            table_row.append('<tr>')
            for item in row:
                table_row.append(f"<td>{item}</td>")
            table_row.append('</tr>')
            return '\n'.join(table_row)

        for i, row in enumerate(data):
            if i==0 and use_header:
                table.append(make_header(row))
            else:
                table.append(add_row(row))
        table.append('</table>')
        table.append('</div>')
        table = '\n'.join(table)
        return table

    def finalize(self, save_dir):
        self._generate_table_of_contents()
        nbformat.write(self.nb, os.path.join(save_dir, self.outname))