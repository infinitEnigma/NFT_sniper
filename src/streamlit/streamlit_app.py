import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import base64
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import requests
import json
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import io, os
import tempfile

def openGoogleSheet():
    # define the scope & credentials & authorize the clientsheet
    scope_app =['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    creds = {google_credentials} # your credentials here
    cred = ServiceAccountCredentials.from_json_keyfile_dict(creds, scope_app)
    client = gspread.authorize(cred)
    return client.open('NFT tracker')


#@st.cache
def load_data():
    # connect & load cmc data
    #coin_data = openGoogleSheet()
    sheet = openGoogleSheet()
    worksheet = sheet.get_worksheet(5)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    df['snapshot_date'] = pd.to_datetime(df['snapshot_date'], format="%Y-%m-%d %H:%M:%S")
    #print(df.resample('W', on='snapshot_date').mean())
    return df



def download_image(img_url,name):
    if not os.path.isfile(f'{name}.png'):
        buffer = tempfile.SpooledTemporaryFile(max_size=1e9)
        r = requests.get(img_url, stream=True)
        if r.status_code == 200:
            downloaded = 0
            filesize = int(r.headers['content-length'])
            for chunk in r.iter_content(chunk_size=1024):
                downloaded += len(chunk)
                buffer.write(chunk)
                #print(downloaded/filesize)
            buffer.seek(0)
            i = Image.open(io.BytesIO(buffer.read()))
            i.save(os.path.join(f'{name}.png'), quality=85)
            print('..image downloaded...')
        buffer.close()



from matplotlib.dates import AutoDateLocator,ConciseDateFormatter

def matplotlib_plot(df_plot, facecolor='#191C23', edgecolor='#666666', linewidth=0.75, linestyle='solid', markerstyle=['o', 'v', '^', '<', '>', '|', 'x']):
    grouped_by_coll = df_plot.groupby('coll_name')
    for name, group in grouped_by_coll:
        fig, ax = plt.subplots(figsize=(20, 7.5), dpi=80, facecolor=facecolor)
        ax.set_facecolor('#0e1117')
        groups = group.groupby("nft_name")
        for j,(nft_name, sub_group) in enumerate(groups):
            plt.plot(sub_group['snapshot_date'], sub_group['nft_floor'], marker=markerstyle[j % len(markerstyle)],
                     linewidth=linewidth-0.25, linestyle=linestyle, label=nft_name)
        locator = AutoDateLocator(minticks=12, maxticks=24)
        formatter = ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_tick_params(which='both', labelcolor='white')
        ax.yaxis.set_tick_params(which='both', labelcolor='white')
        plt.xlabel('Snapshot date', color="white")
        plt.ylabel('NFT floor price in $ADA', color="white")
        title = f'Collection: {name}'
        if len(groups) == 1:
            subtitle = f'NFT: {nft_name} - prices collected from the listings on the jpg.store'
            ax.yaxis.set_major_formatter('₳{x:0.0f}')
            #plt.grid(which='major', axis='both', alpha=0.45, linewidth=linewidth/3)
            #plt.grid(which='minor', axis='both', alpha=0.25, linewidth=linewidth/4)
        else:
            subtitle = f'NFT prices collected from the listings on the jpg.store'
            plt.gca().set_yscale('log')
            ax.yaxis.set_minor_formatter('₳{x:0.0f}')
            ax.yaxis.set_major_formatter('₳{x:0.0f}')
        plt.grid(which='major', axis='both', alpha=0.45, linewidth=linewidth/3)
        plt.grid(which='minor', axis='both', alpha=0.25, linewidth=linewidth/4)

        plt.grid(markersize=0.5)
        plt.text(
            x=0.125, y=0.90, s=title,
            fontsize=20, ha='left', transform=fig.transFigure, color="white"
        )
        plt.text(
            x=0.125, y=0.86, s=subtitle,
            fontsize=16, ha='left', transform=fig.transFigure, color="white"
        )

        plt.legend(loc='best', ncol=1, framealpha=0.5, fancybox=True,
                   labelcolor='white', facecolor='#0e1117', edgecolor='0.4')
        plt.subplots_adjust(top=0.82, wspace=0.3)
        for key, spine in ax.spines.items():
            spine.set_edgecolor(edgecolor)
            spine.set_linewidth(linewidth/2)
        #savefig_file = f'{name}.svg'
        #fig.savefig(savefig_file, dpi=100)
        #st.image(savefig_file)
        st.pyplot(plt)


def main():
    # page layout
    #st.set_page_config(layout="wide")
    st.title('NFT Floor Price App')
    image = 'https://raw.githubusercontent.com/infinitEnigma/infinit3/master/assets/img/posts/multi-author.png')
    st.image(image, width=705) #(image, width = 500)

    st.markdown("""
    This app shows floor prices of few selected NFT collections, collected from [JPG Store](https://jpg.store/)
using [NFTs_︻デ═一](https://replit.com/@infinitEnigma/NFTsniper), which is then stored on Google Sheets and part is shared on
Twitter using automated acc: [NFTs_︻デ═一]](https://twitter.com/JovanSt88177114) and Discord (currently private).
This page shows data collected from Google Sheets in form of dataframes and charts.
""")

    # About
    expander_bar = st.expander("About")
    expander_bar.markdown("""
    * **Python libraries:** streamlit, pandas, matplotlib, gspread
    * **Data source:** [NFTs_︻デ═一](https://replit.com/@infinitEnigma/NFTsniper) [JPG Store](https://jpg.store/).
    """)

    #download_image('https://image-optimizer.jpgstoreapis.com/93416455-a0f4-4cc8-869a-5d9ce71f5d7c?width=350')
    #image = Image.open('image.png')
    #st.image(image)
    # layout - 3 columns
    col1 = st.sidebar
    col2, col3 = st.columns((2,1)) # ratio of space taken

    # sidebar - main panel
    col1.header('Input Options')

    selected_coll = col1.selectbox('Select collection for price chart',
                    ('All', 'Cardano Summit 2021', 'Virtua - Cardano Island Land',
                    'Virtua - Cardano Island vFlects', 'Virtua - Cardano Island Vehicles'))

    # connect & load cmc data
    df = load_data()

    df_table = df.drop(['coll_link', 'coll_image', 'nft_link', 'nft_image'], axis=1)
    df_plot = df.drop(['coll_link', 'coll_image', 'nft_link', 'nft_image'], axis=1)
    df_img = df.drop(['snapshot_date', 'delta_time', 'nft_floor', 'coll_floor'], axis=1)
    if selected_coll != 'All':
        df_table = df_table.query(f'coll_name=="{selected_coll}"')
        df_plot = df_plot.query(f'coll_name=="{selected_coll}"')
        df_img = df_img.query(f'coll_name=="{selected_coll}"')

        im_url = df_img.iloc[-1,2]
        print(im_url)
        download_image(im_url, selected_coll)


        image = Image.open(f'{selected_coll}.png')
        st.image(image) #(image, width = 500)
    st.dataframe(df_table)

    matplotlib_plot(df_plot)

    ls = set(df_plot['nft_name'].tolist())
    selected_nft = col1.selectbox('Select nft for price chart', [*['All'], *ls])
    if selected_nft != 'All':
        df_plot = df_plot.query(f'nft_name=="{selected_nft}"')
        df_table = df_table.query(f'nft_name=="{selected_nft}"')
        df_img = df_img.query(f'nft_name=="{selected_nft}"')

        im_url = df_img.iloc[-1,5]
        print(im_url)
        download_image(im_url, selected_nft)
        image = Image.open(f'{selected_nft}.png')
        st.image(image)
        matplotlib_plot(df_plot)
    st.dataframe(df_table)
    #fig.savefig('line_plot1.png')
    return


main()
