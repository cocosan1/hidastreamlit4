import streamlit as st
# from google.oauth2 import service_account
# from googleapiclient.discovery import build
import os
import plotly.graph_objects as go

#************************************************************棒グラフ
class Graph():
        def make_bar(self, val_list, x_list):
            #可視化
            #グラフを描くときの土台となるオブジェクト
            fig = go.Figure()
            #今期のグラフの追加
            for (val, x) in zip(val_list, x_list):
                fig.add_trace(
                    go.Bar(
                        x=[x],
                        y=[val],
                        text=[round(val/10000) if int(val) >= 10000 else int(val)],
                        textposition="outside", 
                        name=x)
                )
            #レイアウト設定     
            fig.update_layout(
                showlegend=False #凡例表示
            )
            #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
            st.plotly_chart(fig, use_container_width=True) 

        #**********************************************************棒グラフ　今期前期
        def make_bar_nowlast(self, lists_now, lists_last, x_list):
            #可視化
            #グラフを描くときの土台となるオブジェクト
            fig = go.Figure()
            #今期のグラフの追加
            
            for (val_list, name) in zip([lists_now, lists_last], ['今期', '前期']) :
                fig.add_trace(
                    go.Bar(
                        x=x_list,
                        y=val_list,  
                        text=[round(val/10000) if val >= 10000 else int(val) for val in val_list],
                        textposition="outside", 
                        name=name)
                )
            #レイアウト設定     
            fig.update_layout(
                showlegend=True #凡例表示
            )
            #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
            st.plotly_chart(fig, use_container_width=True) 

        #**********************************************************棒グラフ　今期前期 小数
        def make_bar_nowlast_float(self, lists_now, lists_last, x_list):
            #可視化
            #グラフを描くときの土台となるオブジェクト
            fig = go.Figure()
            #今期のグラフの追加
            
            for (val_list, name) in zip([lists_now, lists_last], ['今期', '前期']) :
                fig.add_trace(
                    go.Bar(
                        x=x_list,
                        y=val_list,  
                        text=[round(val, 2) for val in val_list],
                        textposition="outside", 
                        name=name)
                )
            #レイアウト設定     
            fig.update_layout(
                showlegend=True #凡例表示
            )
            #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
            st.plotly_chart(fig, use_container_width=True) 
        
        #*************************************************************棒グラフ　横
         #可視化
        def make_bar_h(self, val_list, label_list, name, title):
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=val_list,
                y=label_list,
                marker_color='#87cefa',
                textfont={'color': '#696969'},
                name=name)
                )
            fig.update_traces(
                textposition='outside',
                texttemplate='%{x:0.2f}%',
                orientation='h'
                )
            # 基準線の追加
            fig.add_shape(
                type="line",
                x0=1,  # 基準線の開始位置 (x座標)
                x1=1,  # 基準線の終了位置 (x座標)
                y0=label_list[0],  # 基準線の開始位置 (y座標)
                y1=label_list[-1],  # 基準線の終了位置 (y座標)
                line=dict(
                    color="red",
                    width=2,
                    dash="dash"  # 破線を使用する場合は "dash" を指定
        )
    )
            fig.update_layout(
                title=title,
                width=500,
                height=2500,
                plot_bgcolor='white'
                )
            #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
            st.plotly_chart(fig, use_container_width=True) 

        #**********************************************************折れ線
        def make_line(self, df_list, name_list, x_list):

            #グラフを描くときの土台となるオブジェクト
            fig = go.Figure()
            #今期のグラフの追加

            for (df, name) in zip(df_list, name_list):

                fig.add_trace(
                go.Scatter(
                    x=x_list, #strにしないと順番が崩れる
                    y=df,
                    mode = 'lines+markers+text', #値表示
                    text=[round(val/10000) if val >= 10000 else int(val) for val in df],
                    textposition="top center", 
                    name=name)
                    )  

            #レイアウト設定     
            fig.update_layout(
                showlegend=True #凡例表示
            )
            #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
            st.plotly_chart(fig, use_container_width=True) 
        
                #**********************************************折れ線　non_xlist    
        def make_line_nonXlist(self, df_list, name_list):
            #グラフを描くときの土台となるオブジェクト
            fig = go.Figure()
            #今期のグラフの追加

            for (df, name) in zip(df_list, name_list):

                fig.add_trace(
                go.Scatter(
                    x=['10月', '11月', '12月', '1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月'], #strにしないと順番が崩れる
                    y=df,
                    mode = 'lines+markers+text', #値表示
                    text=[round(val/10000) if val >= 10000 else int(val) for val in df],
                    textposition="top center", 
                    name=name)
                    )  

            #レイアウト設定     
            fig.update_layout(
                showlegend=True #凡例表示
            )
            #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
            st.plotly_chart(fig, use_container_width=True) 
            
        #***************************************************************円
        def make_pie(self, vals, labels):

            # st.write(f'{option_category} 構成比(今期)')
            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=labels,
                        values=vals
                        )])
            fig.update_layout(
                showlegend=True, #凡例表示
                height=290,
                margin={'l': 20, 'r': 60, 't': 0, 'b': 0},
                )
            fig.update_traces(textposition='inside', textinfo='label+percent') 
            #inside グラフ上にテキスト表示
            st.plotly_chart(fig, use_container_width=True) 
            #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅




# def get_file_from_gdrive(cwd, file_name):
#         #*********email登録状況のチェック
#         # Google Drive APIを使用するための認証情報を取得する
#         creds_dict = st.secrets["gcp_service_account"]
#         creds = service_account.Credentials.from_service_account_info(creds_dict)

#         # Drive APIのクライアントを作成する
#         #API名（ここでは"drive"）、APIのバージョン（ここでは"v3"）、および認証情報を指定
#         service = build("drive", "v3", credentials=creds)

#         # 指定したファイル名を持つファイルのIDを取得する
#         #Google Drive上のファイルを検索するためのクエリを指定して、ファイルの検索を実行します。
#         # この場合、ファイル名とMIMEタイプを指定しています。
#         query = f"name='{file_name}' and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
#         #指定されたファイルのメディアを取得
#         results = service.files().list(q=query).execute()
#         items = results.get("files", [])

#         if not items:
#             st.warning(f"No files found with name: {file_name}")
#         else:
#             # ファイルをダウンロードする
#             file_id = items[0]["id"]
#             file = service.files().get(fileId=file_id).execute()
#             file_content = service.files().get_media(fileId=file_id).execute()

#             # ファイルを保存する
#             file_path = os.path.join(cwd, 'data', file_name)
#             with open(file_path, "wb") as f:
#                 f.write(file_content)