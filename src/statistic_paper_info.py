import pubmed_parser as pp
import lib_pubmed_oa_parser2 as pp2


def extract_paper_info(path):
    len_figure_caption = []
    len_table_caption = []

    fig_ids = []
    table_ids = []

    num_figure = 0
    num_table = 0

    out_paragraph = pp.parse_pubmed_paragraph(path)

    out_figure = pp2.parse_pubmed_caption2(path)
    out_table = pp2.parse_pubmed_table2(path)

    wo_caption = False

    if out_figure is not None:
        for caption in out_figure:
            if caption['fig_caption'] is None:
                wo_caption = True
                len_figure_caption.append(0)
            else:
                len_figure_caption.append(len(caption['fig_caption']))
        for figure in out_figure:
            fig_ids.append(figure['fig_id'])
        num_figure = len(out_figure)

    if out_table is not None:
        for caption in out_table:
            if caption['table_caption'] is None:
                wo_caption = True
                len_figure_caption.append(0)
            else:
                len_table_caption.append(len(caption['table_caption']))
        for table in out_table:
            table_ids.append(table['table_id'])
        num_table = len(out_table)

    ref_count = {}
    for paragraph in out_paragraph:
        for ref_id in paragraph['reference_ids']:
            if ref_id in fig_ids or ref_id in table_ids:
                ref_count[ref_id] = ref_count.get(ref_id, 0) + 1

    paper_info = {'num_figure': num_figure,
                  'num_table': num_table,
                  'num_table+figure': num_figure + num_table,
                  'len_figure_caption': len_figure_caption,
                  'len_table_caption': len_table_caption,
                  'ref_count': ref_count,
                  'wo_caption': wo_caption
                  }

    return paper_info


def test():

    path = '../data/pmc/PMC450293.xml'
    paper_info = extract_paper_info(path)
    return paper_info


test()
