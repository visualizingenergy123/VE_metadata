#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 09:33:34 2023

@author: hcliffo
"""

import gspread as gs
import pandas as pd
from datetime import date
import re
import sys
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)


def truncate_string(string):  

    new_input = ""
    for i, letter in enumerate(string):
        if i % 180 == 0:
            new_input += '\n'
        new_input += letter
    
    # this is just because at the beginning too a `\n` character gets added
    new_input = new_input[1:] 
    return new_input

def wrap(text,length):
  string = re.compile(f'(.{{1,{length}}})(?=\\b)')
  return string.findall(text)


def create_metadata(drive):   

    meta_id =  drive.ListFile({'q':"'1yhOaxubiipCh9TZ7pS_lV_DkOJ0VvcMX' in parents and trashed=false", 
                                'includeItemsFromAllDrives': True, 
                                'supportsAllDrives': True}).GetList()
    list_of_meta_names = [file['title'][:-4] for file in meta_id]
    
    gc = gs.service_account(filename='VE_key.json')
    
    sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1as3ZNs07NKuT1uX6m_UfPUWLALHp_picGQcklcz_zTA/edit#gid=2126422537')
    
    ws = sh.worksheet('Sheet1')
    
    df = pd.DataFrame(ws.get_all_records())
    
    today = date.today()
    df = df.replace([''], [None])
    
    df['Time span'].replace({'nan':'Not Applicable'}, inplace=True)
    
    
    for n,row in df.iterrows():
        viz_id = row['Visualization ID']
        viz_title = row['Visualization Title']
        meta_filename = "{viz_id}_meta".format(viz_id=viz_id)
        if not meta_filename in list_of_meta_names:
            print('Creating metadata for '+viz_id)
            viz_title =  viz_title.replace(',','')
            time_span = row['Time span']
            try:
                time_span =  time_span.replace(',',';')
            except:
                pass
            
            
            text = \
u"""#visualizingenergy.org
#Contact: vizen@bu.edu
#
#Title: {viz_title}
#Time span: {time_span}""".format(today=today,viz_title=viz_title,time_span=time_span)
            
            var1 = row[4:10]
            var2 = row[10:16]
            var3 = row[16:22]
            var4 = row[22:28]
            
            list_var = []
            for n,var in enumerate([var1,var2,var3,var4]):
                if not var.isnull().all():
                    var.fillna('None', inplace=True)
                    var_name = var[0]
                    var_name =  var_name.replace(',','')
                    source = var[2]
                    source = source.replace(',',';')
                    source_link = var[3]
                    source_link = source_link.replace('<br>',';')
                    if source_link != 'None':
                        source_link = source_link.replace('<br> ','\n\n')
                        source_link = source_link.replace('<br>','\n\n')
                    var_accessed = var[1]
                    try:
                        if (var_accessed != 'None') & (var_accessed != 'not applicable'):
                            var_accessed = pd.to_datetime(var_accessed)
                            var_accessed = var_accessed.strftime('%Y-%m-%d')
                        else:
                            var_accessed = 'not applicable'
                    except:
                       
                        var_accessed = 'not applicable'
                            
                    description = var[4]
                    description = description.replace(',',';')
                    description = description.replace('<br>',' ')
                    if description != 'None':
                        description = description.replace('<br> ',';')
                        description = description.replace('<br>',';')
          
                    links = var[5]
                    links = links.replace('<br>',';')
                    
                    var_info ="""
#----------------------------------------------------------------
#Variable: {var_name}
#Source: {source}
#Source link: {source_link}
#Data accessed: {var_accessed}""".format(var_name=var_name,
                               source=source,
                               source_link=source_link,
                               var_accessed=var_accessed)
                    text = text + var_info
            
            
                    if description != 'None':
                        descript_info= """
#Description: {description}""".format(description=description)
        
                        descript_info = wrap(descript_info,170)
                        
                        text = text + ('\n').join(descript_info)
        
                    if links != 'None':
                        links_info ="""
#Additional links: {links}""".format(links=links)
                        text = text + links_info
                           
                   
                    
            text = text+"""
#================================================================"""
            f = drive.CreateFile({
                'title': "{viz_id}_meta.txt".format(viz_id=viz_id),
                'parents': [{
                    'kind': 'drive#fileLink',
                    'id': '1yhOaxubiipCh9TZ7pS_lV_DkOJ0VvcMX'}]})
            
            f.SetContentString(text)
            f.Upload(param={'supportsTeamDrives': True})
    
                    
            f = drive.CreateFile({
                'title': "{viz_id}_meta.csv".format(viz_id=viz_id),
                'parents': [{
                    'kind': 'drive#fileLink',
                    'id': '1yhOaxubiipCh9TZ7pS_lV_DkOJ0VvcMX'}]})
        
            f.SetContentString(text)
            f.Upload(param={'supportsTeamDrives': True})
    
    
            

create_metadata(drive)
            
            
            
        
        
        
        
        
        
