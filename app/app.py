from io import BytesIO
import base64

import streamlit as st
import boka_tools as bt
import pandas as pd
import numpy as np

ENGINE = bt.server_connect('10.64.32.62', 'EngDep')


@st.cache
def get_gint_data():

    with ENGINE.connect() as conn:
        results = conn.execute('SELECT PointID, Area, Box, Type FROM POINT WHERE Area IS NOT NULL')
        pointids = [row for row in results]

    df = pd.DataFrame(pointids, columns=['PointID', 'Area', 'Box', 'Type'])

    areas = np.sort(df.Area.unique())

    return areas, df


def get_download_link(fig: object, pointid: str) -> str:
    """
    Generates a link allowing the data from a matplotlib pdf to be downloaded
    """
    output = BytesIO()
    fig.savefig(output, format='pdf')
    output.seek(0)
    b64 = base64.b64encode(output.getvalue()).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="{pointid}.pdf">Download PDF report</a>'


@st.cache(allow_output_mutation=True)
def parse_gef(file):
    gef = bt.soil_investigation.ParseGEF(string=file.getvalue())
    plot_props = bt.soil_investigation.boiler_plates.gef.standard_gef_plot(gef)

    return plot_props


logo = st.sidebar.selectbox('Logo', ['BPJV', 'Boskalis', 'Hydronamic'])
select = st.sidebar.selectbox('Data Source', ['gINT', 'GEF'])

if select == 'GEF':
    file = st.sidebar.file_uploader('GEF File', encoding='ANSI', type=['GEF', 'gef'])

    if file is not None:
        plot_props_ = parse_gef(file)

elif select == 'gINT':
    file = None
    gint_type = st.sidebar.selectbox('plot type', ['standard', 'su', 'bh-cpt', 'bh'])

    areas, point_ids = get_gint_data()
    select_area = st.sidebar.selectbox('Area', areas, index=1)

    df_filtered_CPT = point_ids[(point_ids.Area == select_area) & (point_ids.Type == 'CPT')]
    df_filtered_BH = point_ids[(point_ids.Area == select_area) & (point_ids.Type == 'RO')]

    if gint_type == 'bh-cpt':
        select_pid = st.sidebar.selectbox('PointID', df_filtered_CPT.PointID.values)
        select_pid_bh = st.sidebar.selectbox('PointID - BH', df_filtered_BH.PointID.values)
        plot_props_ = bt.soil_investigation.boiler_plates.gint.gint_plot_cpt_lab_bh(ENGINE, select_pid, select_pid_bh)

    elif gint_type == 'standard':
        select_pid = st.sidebar.selectbox('PointID', df_filtered_CPT.PointID.values)
        plot_props_ = bt.soil_investigation.boiler_plates.gint.standard_gint_cpt_plot(ENGINE, select_pid)

    elif gint_type == 'su':
        select_pid = st.sidebar.selectbox('PointID', df_filtered_CPT.PointID.values)
        plot_props_ = bt.soil_investigation.boiler_plates.gint.su_gint_cpt_plot(ENGINE, select_pid)

    elif gint_type == 'bh':
        select_pid_bh = st.sidebar.selectbox('PointID - BH', df_filtered_BH.PointID.values)
        plot_props_ = bt.soil_investigation.boiler_plates.gint.standard_gint_bh_plot(ENGINE, select_pid_bh)


prep_by = st.sidebar.text_input('Prepared by', value='MBET')
chk_by = st.sidebar.text_input('Checked by', value='MBET')
apr_by = st.sidebar.text_input('Approved by', value='MBET')


if "plot_props_" in globals():
    pointid = plot_props_['info']['pointid'][0]

    plot_props_['info']['version_values'][2] = prep_by
    plot_props_['info']['version_values'][3] = chk_by
    plot_props_['info']['version_values'][4] = apr_by

    if logo == "Boskalis":
        ext = '.jpg'
    else:
        ext = '.png'

    plot_props_['layout']['logo'] = './logo/'+logo+ext

    fig = bt.soil_investigation.plot_si_results(plot_props_)
    st.markdown(get_download_link(fig, pointid), unsafe_allow_html=True)
    st.write(fig)

