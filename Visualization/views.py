from django.shortcuts import render
from plotly.offline import plot
import plotly.graph_objects as go
from UploadData.models import *
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np



def visualization(request, fid):
    file = controller_file.objects.get(file_id = fid)
    # set titles   
    titles = ['Acceleration for equal velocities (RL)']
    subplot_titles = ['ego speed = {} m/s'.format(2*i) for i in range(16)]
    titles.extend(subplot_titles)
    
    fig = make_subplots(rows=13, cols=4, start_cell="top-left",
                    specs=[[{"rowspan": 3, "colspan": 4},None,None,None],
                            [None,None,None,None],
                            [None,None,None,None],
                            [None,None,None,None],
                            [{},{},{},{}],
                            [{},{},{},{}],
                            [{},{},{},{}],
                            [{},{},{},{}],
                            [{},{},{},{}],
                            [{},{},{},{}],
                            [{},{},{},{}],
                            [{},{},{},{}],
                            [{},{},{},{}]],
                    horizontal_spacing=0.1,
                    vertical_spacing=0.02,
                    subplot_titles=titles
                    )
    
    # Data for the plots
    data = controller_data.objects.filter(file_id = fid)
    space_gap = [i['space_gap'] for i in data.values('space_gap')]
    accel = [i['accel'] for i in data.values('accel')]
    ego_speed = [i['ego_speed'] for i in data.values('ego_speed')]
    leader_speed = [i['leader_speed'] for i in data.values('leader_speed')]

    # 1. Equilibrium plot
    # space gap on the y-axis and speed on the x-axis.
    # filter the data when leader speed equals to ego_speed
    e_space_gap = []
    e_accel = []
    e_speed = []
    for i in range(len(space_gap)):
        if leader_speed[i] == ego_speed[i]:
            e_space_gap.append(space_gap[i])
            e_accel.append(accel[i])
            e_speed.append(leader_speed[i])

    fig1 = go.Heatmap(
                    z=e_accel,
                    y=e_space_gap,
                    x=e_speed,
                    colorscale='Viridis',
                    colorbar={"title": 'Acceleration / m/s2',
                              "title.side": 'right',
                              'titlefont.size': 10,
                              'len':0.21,
                              'y':0.9,
                              'tickfont.size':10})

    # filter the data when speed close to zero
    z_space_gap = []
    z_speed = []
    for i in range(len(e_space_gap)):
        if abs(e_accel[i]) < 0.1:
            z_space_gap.append(e_space_gap[i])
            z_speed.append(e_speed[i])
    
    fig2 = go.Scatter(x=z_speed, 
                      y=z_space_gap,
                      line=dict(color='black', width=0.5),
                      name="equilibrium curve"
                      )
    
    fig.add_trace(fig1,row=1, col=1)
    fig.add_trace(fig2,row=1, col=1)
    fig.update_xaxes(title_text='speed v m/s',
                     title_font_size = 10,
                     range=[0,30], row=1, col=1)
    fig.update_yaxes(title_text='gap s/m',
                     title_font_size = 10,
                     range=[0,100],row=1, col=1)
    
    # 2. Phase Space Cross Sections Plot: 
    # space gap on the y-axis and lead speed on the x-axis.
    # add title
    for spd in range(16):
        # filter data
        tmp_space_gap = []
        tmp_lead_speed = []
        tmp_accel = []
        for i in range(len(space_gap)):
            if ego_speed[i] == 2*spd:
                tmp_space_gap.append(space_gap[i])
                tmp_accel.append(accel[i])
                tmp_lead_speed.append(leader_speed[i])
        # make plot
        subplt = go.Heatmap(
                    z=tmp_accel,
                    y=tmp_space_gap,
                    x=tmp_lead_speed,
                    colorscale='Viridis',
                    colorbar={"title": 'Acceleration / m/s2',
                              "title.side": 'right',
                              'titlefont.size': 10,
                              'len':0.052,
                              'thickness':15,
                              'y':0.66 - (spd//4)*0.08,
                              'x':0.175+(spd%4)*0.275,
                              'tickfont.size':10})
        fig.add_trace(subplt,row=spd//4+5, col=(spd%4)+1)
        fig.add_vline(spd*2,row=spd//4+5, col=(spd%4)+1,line_width=0.6, line_dash="dash", line_color="black")
        fig.update_xaxes(title_text='leader speed v m/s', 
                         title_font_size = 10,
                         range=[0,30],
                         row=spd//4+5, 
                         col=(spd%4)+1,
                         tickfont=dict(size=10),
                         title_standoff=5),
        fig.update_yaxes(tickfont=dict(size=10),
                    row=spd//4+5,
                    range=[0,100],
                    col=(spd%4)+1,)
        
        # filter the data when speed close to zero
        z_space_gap = []
        z_speed = []
        for i in range(len(tmp_accel)):
            if abs(tmp_accel[i]) < 0.1:
                z_space_gap.append(tmp_space_gap[i])
                z_speed.append(tmp_lead_speed[i])
        
        zero_accel = go.Scatter(x=z_speed, 
                        y=z_space_gap,
                        line=dict(color='black', width=0.5),
                        name="equilibrium curve"
                        )
        fig.add_trace(zero_accel,row=spd//4+5, col=(spd%4)+1)
    
    # 3. Lane Change Heat Map: 
    # y-axis will be the original space gap, and the x-axis will be the space gap
    for spd in range(16):
        # filter data
        tmp_accel = []
        for i in range(len(space_gap)):
            if ego_speed[i] == 2*spd and ego_speed[i] == leader_speed[i]:
                tmp_space_gap.append(space_gap[i])
                tmp_accel.append(accel[i])

        tmp_accel = np.asarray([tmp_accel])
        accel_delta = tmp_accel - tmp_accel.T
        # make plot
        subplt = go.Heatmap(
                    z=accel_delta,
                    colorscale='Viridis',
                    colorbar={"title": 'Acceleration DT/ m/s2',
                              "title.side": 'right',
                              'titlefont.size': 10,
                              'len':0.052,
                              'thickness':15,
                              'y':0.26 - (spd//4)*0.08,
                              'x':0.17+(spd%4)*0.28,
                              'tickfont.size':10})
        fig.add_trace(subplt,row=spd//4+10, col=(spd%4)+1)
        fig.update_xaxes(title_font_size = 10,
                         title_text='space gap /m',
                         tickfont=dict(size=10),
                         range=[0,100],
                         row=spd//4+10, 
                         col=(spd%4)+1,
                         title_standoff=5
                         )
        fig.update_yaxes(tickfont=dict(size=10),
                         range=[0,100],
                         row=spd//4+10, 
                         col=(spd%4)+1,)

    # whole figure setup 
    fig.update_layout(showlegend=False)
    fig.layout.height = 2300
    fig.layout.width = 1000
    fig.update_annotations(font=dict(color='black',size=12)) # subtitle font size
    # make space for explanation / annotation
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))

    # add figure title
    fig.add_annotation(dict(font=dict(color='black',size=12),
                                        x=0.5,
                                        y=0.7,
                                        showarrow=False,
                                        text="Acceleration as function of phase space(RL)",
                                        textangle=0,
                                        xanchor='center',
                                        xref="paper",
                                        yref="paper"))
    fig.add_annotation(dict(font=dict(color='black',size=12),
                                        x=0.5,
                                        y=0.3,
                                        showarrow=False,
                                        text="Lane Change Heat Map",
                                        textangle=0,
                                        xanchor='center',
                                        xref="paper",
                                        yref="paper"))
    chart = fig.to_html()
    return render(request, 'visualization.html', 
                  context={'chart': chart,'file':file})
