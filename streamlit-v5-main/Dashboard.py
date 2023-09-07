import streamlit as st
from api import API
from datetime import date, datetime, timedelta
import plotly.express as px
import pandas as pd
import numpy as np
import os
from Download_special import download_button

BUILTIN_KEYWORDS_URL = "https://docs.google.com/spreadsheets/d/1tYX4LhPLGzjyhCcjd1chPS4xmJcvqRyMWTvsxSlOdIo/edit?usp=sharing"
API_KEY_URL = "https://docs.google.com/spreadsheets/d/19HqWX4soa_ODZMn2V1XV0lfkgovU10Quvu1ysr2fwlo/edit?usp=sharing"
api_keys_df = pd.read_csv(API_KEY_URL.replace("/edit?usp=sharing", "/export?format=csv&gid=0"))

AGE_GROUP = {
    1: "0-12",
    2: "13-18",
    3: "19-24",
    4: "25-29",
    5: "30-34",
    6: "35-39",
    7: "40-44",
    8: "45-49",
    9: "50-54",
    10: "55-59",
    11: "60+",
}

def break_list(input_list):
    output_list = []
    sublist = []

    for item in input_list:
        sublist.append(item)
        if len(sublist) == 5:
            output_list.append(sublist)
            sublist = []

    if sublist:
        output_list.append(sublist)

    return output_list


def name_calculate(device, gender, age):
    output = ""

    if gender != "":output += gender
    if device != "":output += (device if output == "" else f"-{device}")
    if age != []:
        try:output += ((','.join([AGE_GROUP[int(i)] for i in age]) if output == "" else f"-{','.join([AGE_GROUP[int(i)] for i in age])}") if type(age) == list else age)
        except:output += ((','.join([i for i in age]) if output == "" else f"-{','.join([i for i in age])}") if type(age) == list else age)
    if output == "":output = "All"
    return output

def constuct_chart(start_date:date, end_date:date, genders:list, devices:list, ages:list, timeunit:str, keyword_group:list, keywords:list, Denominator:float):
    global api_keys_df    
    tabs = st.tabs(keyword_group)

    instructions_placeholder.empty()

    keywords_groups_ = break_list(keyword_group)
    keywords_ = break_list(keywords)

    main_cnt = 0
    key = -1

    for id, secret in api_keys_df.values.tolist()[::-1]:
        try:          
            for keyword_group, keywords in zip(keywords_groups_, keywords_):
                all_dfs = []
                main_cnt += len(keyword_group)

                search = API(id, secret)
                search.setStartDate(start_date.isoformat())
                search.setEndDate(end_date.isoformat())
                search.setTimeUnit(timeunit)
                search.setDevice(device_options[devices[0]] if len(devices) == 1 else '')
                search.setGender(gender_options[genders[0]] if len(genders) == 1 else '')
                search.setAges([age_options[i][0] for i in ages if not "All" in ages])
                search.setKeywordGroups(keyword_group, keywords)
                result = search.sendRequest()

                for cnt, tab in enumerate(tabs[main_cnt-min(len(keyword_group), 5):main_cnt]):
                    df = pd.DataFrame(result['results'][cnt]["data"])
                    df["ratio"] = df["ratio"]/Denominator
                    df.rename(columns={'period':"Date", "ratio": "All"}, inplace=True)

                    main_df = df.copy()
                    main_df["Date"] = pd.to_datetime(main_df["Date"])
                    all_dfs.append(main_df)

                    df = df.melt('Date', var_name='All', value_name='Ratio')
                    fig = px.line(df, x="Date", y="Ratio", color='All', range_y=(0, 100))
                    tab.plotly_chart(fig)

                for cnt, device in enumerate((["Mobile", "PC"] if 'All' in devices else devices)):
                    search = API(id, secret)
                    search.setStartDate(start_date.isoformat())
                    search.setEndDate(end_date.isoformat())
                    search.setTimeUnit(timeunit)
                    search.setDevice(device_options[device])
                    search.setGender(gender_options[genders[0]] if len(genders) == 1 else '')
                    search.setAges([age_options[i][0] for i in ages if not "All" in ages])
                    search.setKeywordGroups(keyword_group, keywords)
                    result = search.sendRequest()
                    
                    if cnt == 0:
                        dfs = [df:=(pd.DataFrame(result['results'][cnt]["data"]).rename(columns={'period':"Date", "ratio": device}, inplace=False)) for cnt, _ in enumerate(tabs[main_cnt-min(len(keyword_group), 5):main_cnt])]
                        for d in dfs:d[device] = d[device]/Denominator

                    else:
                        
                        for cnt, df in enumerate(dfs):df[device] = pd.DataFrame(result['results'][cnt]["data"])["ratio"]/Denominator
                    for main_df, df in zip(all_dfs, dfs):
                        main_df[name_calculate(device, gender_options[genders[0]] if len(genders) == 1 else '', [age_options[i][0] for i in ages if not "All" in ages])] = df[device]

                for df, tab in zip(dfs, tabs[main_cnt-min(len(keyword_group), 5):main_cnt]):
                    df = df.melt('Date', var_name='Devices', value_name='Ratio')
                    fig = px.line(df, x="Date", y="Ratio", color='Devices', color_discrete_map={'PC': 'blue', 'Mobile': 'red'}, range_y=(0, 100))
                    tab.plotly_chart(fig)

                for cnt, gender in enumerate((["Female", "Male"]  if 'All' in genders else genders)):
                    search = API(id, secret)
                    search.setStartDate(start_date.isoformat())
                    search.setEndDate(end_date.isoformat())
                    search.setTimeUnit(timeunit)
                    search.setDevice(device_options[devices[0]] if len(devices) == 1 else '')
                    search.setGender(gender_options[gender])
                    search.setAges([age_options[i][0] for i in ages if not "All" in ages])
                    search.setKeywordGroups(keyword_group, keywords)
                    result = search.sendRequest()
                    # print(result)

                    if cnt == 0:
                        dfs = [pd.DataFrame(result['results'][cnt]["data"]).rename(columns={'period':"Date", "ratio": gender}, inplace=False) for cnt, _ in enumerate(tabs[main_cnt-min(len(keyword_group), 5):main_cnt])]
                        for d in dfs:d[gender] = d[gender]/Denominator
                    else:
                        
                        for cnt, df in enumerate(dfs):df[gender] = pd.DataFrame(result['results'][cnt]["data"])["ratio"]/Denominator
                    for main_df, df in zip(all_dfs, dfs):
                        main_df[name_calculate(device_options[devices[0]] if len(devices) == 1 else '', gender, [age_options[i][0] for i in ages if not "All" in ages])] = df[gender]

                for df, tab in zip(dfs, tabs[main_cnt-min(len(keyword_group), 5):main_cnt]):
                    df = df.melt('Date', var_name='Gender', value_name='Ratio')
                    fig = px.line(df, x="Date", y="Ratio", color='Gender', color_discrete_map={'Male': 'blue', 'Female': '#AA336A'}, range_y=(0, 100))
                    tab.plotly_chart(fig)
                
                try:
                    for cnt, age in enumerate((['0-12', '13-18', '19-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60+'] if 'All' in ages else ages)):
                        search = API(id, secret)
                        search.setStartDate(start_date.isoformat())
                        search.setEndDate(end_date.isoformat())
                        search.setTimeUnit(timeunit)
                        search.setDevice(device_options[devices[0]] if len(devices) == 1 else '')
                        search.setGender(gender_options[genders[0]] if len(genders) == 1 else '')
                        search.setAges(age_options[age])
                        search.setKeywordGroups(keyword_group, keywords)
                        result = search.sendRequest()

                        # print(pd.DataFrame(result['results'][0]["data"]))

                        if cnt == 0:
                            dfs = [pd.DataFrame(result['results'][cnt]["data"]).rename(columns={'period':"Date", "ratio": age}, inplace=False) for cnt, _ in enumerate(tabs[main_cnt-min(len(keyword_group), 5):main_cnt])]
                        for d in dfs:
                            try:d[age] = d[age]/Denominator
                            except:pass
                        else:
                            for cnt, df in enumerate(dfs):
                                temp = pd.DataFrame(result['results'][cnt]["data"]).rename(columns={'period':"Date", "ratio": age}, inplace=False)
                                try:
                                    temp[age] = temp[age]/Denominator
                                    dfs[cnt] = pd.merge(df, temp, on='Date', how='outer')
                                except:pass

                        # for df in dfs:
                        #     df[age] = df[age].fillna(0).astype(int).round().replace(0, np.nan)

                        # print(df)
                        # df[age]

                        # main_df[age] = None
                    for cnt, (main_df, df) in enumerate(zip(all_dfs, dfs)):
                        try:
                            dfs[cnt]["Date"] = pd.to_datetime(df["Date"])
                            all_dfs[cnt] = pd.merge(main_df, dfs[cnt], on='Date', how='outer')
                        except:pass

                    for df, tab in zip(dfs, tabs[main_cnt-min(len(keyword_group), 5):main_cnt]):
                        try:
                            df = df.melt('Date', var_name='Age', value_name='Ratio')
                            order = {'0-12':0, '13-18':1, '19-24':2, '25-29':3, '30-34':4, '35-39':5, '40-44':6, '45-49':7, '50-54':8, '55-59':9, '60+':10}
                            df["Age"] = df["Age"].map(order)
                            df = df.sort_values(['Date', "Age"])
                            df["Age"] = df["Age"].replace({v: k for k, v in order.items()})
                            df = df.reset_index()

                            fig = px.line(df, x="Date", y="Ratio", color='Age', range_y=(0, 100))
                            tab.plotly_chart(fig, height=600, use_container_width=True)
                        except:pass

                except Exception as e:
                    for df, tab in zip(dfs, tabs[main_cnt-min(len(keyword_group), 5):main_cnt]):
                        tab.warning("Data not found in Age!")

                    print(e)


                for main_df, tab, key_word in zip(all_dfs, tabs[main_cnt-min(len(keyword_group), 5):main_cnt], keyword_group):
                    key += 1
                    main_df.to_excel(f"{key_word}.xlsx", index=False)
                    
                    with open(f'{key_word}.xlsx', 'rb') as f:
                        s = f.read()
                    download_button_str = download_button(s, f'{key_word}.xlsx', 'Download Data')
                    tab.markdown(download_button_str, unsafe_allow_html=True)

                    os.remove(f'{key_word}.xlsx')

            break
        except:
            api_keys_df = api_keys_df.apply(np.roll, shift=-1)
            api_keys_df.to_excel("api_keys.xlsx", index=False)

            print(id, secret)


keywords_default_df = pd.read_csv(BUILTIN_KEYWORDS_URL.replace("/edit?usp=sharing", "/export?format=csv&gid=0"))
keywords_default_df.values.tolist()
keywords_default = {}
for key, value in keywords_default_df.values.tolist():
    keywords_default[key] = value

st.title("Naver Keyword Trends")
st.sidebar.title("Select Filters")
# For the title "Naver Keyword Trends"
st.markdown("""
<style>
.center-title {
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 24px;  # Optional: adjust font size as needed
}
</style>
<div class="center-title">
    Naver Keyword Trends
</div>
""", unsafe_allow_html=True)

# Your application's content goes here...

# For the "Made with xxx Team"
st.markdown("""
<style>
.center-footer {
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 18px;  # Optional: adjust font size as needed
}
</style>
<div class="center-footer">
    Made with xxx Team
</div>
""", unsafe_allow_html=True)

instructions_placeholder = st.empty()

instructions_placeholder.markdown("""
<style>
    .instr-box {
        border-radius: 10px;
        padding: 10px;
        background-color: #FFD1D1;
    }
</style>
<div class="instr-box">
To use custom keyword group:
    a. Select "Insert Custom Keyword Group" under "Select Builtin Keywords"
    b. Key in a title for your Keyword Group.
    c. Key in your keywords (not more than 20 and separated by a comma ",") in the Keywords section.
    d. Make your selections to the remaining fields and click the "submit button"
</div>
""", unsafe_allow_html=True)

keywords_options = list(keywords_default.keys())
keywords_options_withother = list(keywords_default.keys())
keywords_options_withother.append("Insert custom keyword group")
keyword_selection = st.sidebar.multiselect("Select Builtin Keywords", keywords_options_withother)

# Check if "Other" is selected
show_textboxes = "Insert custom keyword group" in keyword_selection

# Create a placeholder for the textboxes
textbox_placeholder = st.empty()

# Display textboxes conditionally
if show_textboxes:
    Keyword_group = st.sidebar.text_input("Keyword Group")
    Keywords = st.sidebar.text_area("Keywords")
else:
    textbox_placeholder.empty()  # Clear the placeholder

# Date range selection
start_date = st.sidebar.date_input('Start Date', min_value=date(2016, 1, 1), value=(datetime.today().replace(day=1)).date(), max_value=(date.today()- timedelta(days=1)))
end_date = st.sidebar.date_input('End Date', min_value=date(2016, 1, 1), max_value=date.today())

st.markdown("Made with ❤️ by the APAC SEO Team")

# Data type selection
data_options = ['date', 'week', 'month']
selected_data = st.sidebar.selectbox('Select Data Type', data_options)

# Gender selection
gender_options = {'All':'', 'Male':'m', 'Female':'f'}
selected_gender = st.sidebar.multiselect('Select Gender', gender_options.keys(), default=["All"])

# Device selection
device_options = {'All': '', 'PC': 'pc', 'Mobile': 'mo'}
selected_device = st.sidebar.multiselect('Select Device', device_options.keys(), default=["All"])

# Age group selection
age_options = {
    'All': [],
    '0-12': ['1'],
    '13-18': ['2'],
    '19-24': ['3'],
    '25-29': ['4'],
    '30-34': ['5'],
    '35-39': ['6'],
    '40-44': ['7'],
    '45-49': ['8'],
    '50-54': ['9'],
    '55-59': ['10'],
    '60+': ['11'],
}
selected_age = st.sidebar.multiselect('Select Age Group', age_options, default=["All"])

# Denominator = st.sidebar.text_input("Denominator: ", value="1")
Denominator = 1

submit = st.sidebar.button('Submit')


if submit:
    
    if "Insert custom keyword group" in keyword_selection:
        keywordgroup_process = keyword_selection
        keywordgroup_process.extend([i.removeprefix(" ").removesuffix(" ") for i in Keyword_group.split(",")])
        keywordgroup_process.remove("Insert custom keyword group")

        keyword_process = [keywords_default[k].split(",") for k in keyword_selection]
        keyword_process.extend([k.split(",") for k in Keywords.replace("\\", "/").split("/")])
    else:
        keywordgroup_process = keyword_selection
        keyword_process = [keywords_default[k].split(",") for k in keyword_selection]

    constuct_chart(start_date, end_date, selected_gender, selected_device, selected_age, selected_data, keywordgroup_process, keyword_process, float(Denominator))
