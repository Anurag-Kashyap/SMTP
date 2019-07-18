import smtplib
import pandas as pd
from datetime import date
#import numpy as np
#import operator

#reading the file with all the sender and receiver mail IDs
receivers = pd.read_csv('ReceiversList.csv')
df = pd.read_csv('MailConfig.csv')

#reading the data file
df1 = pd.read_csv('SalesControlChart.csv')
df2 = pd.read_csv('WeeklySales.csv')

#Brand 'nan' are labelled as 'NON-BRANDED'
df1['Brand'].fillna("NON-BRANDED", inplace=True)
df2['Brand'].fillna("NON-BRANDED", inplace=True)

#latestWeek = df2['Weeknumber'].max()
latestWeek = 15
print(latestWeek)

#building the primary key
df1['Key'] = df1['Brand'] + ' at ' + df1['RetailerName']
df2['Key'] = df2['Brand'] + ' at ' + df2['RetailerName']
receivers['Key'] = receivers['Brand'] + ' at ' + receivers['RetailerName']

#droping the unwanted and repeated columns from the SalesControlChart
df1 = df1.drop(['Brand', 'RetailerName', 'AverageSales1', 'Standard Deviation1'], axis=1)
receivers = receivers.drop(['Brand', 'RetailerName'], axis=1)

#mapping both the tables together
df_map = pd.merge(df2, df1, how='left', left_on = 'Key', right_on = 'Key')

df_map['UCL_check'] = df_map['Sum of Sales'] < df_map['UCLmean+sigma1']
df_map['LCL_check'] = df_map['Sum of Sales'] > df_map['LCLmean-sigma1']
df_map['UCL_check'] = df_map['UCL_check'].astype(int)
df_map['LCL_check'] = df_map['LCL_check'].astype(int)
#print(df_map['UCL_check'].head())

#df_map.to_csv('check3.csv')

df_checker = pd.DataFrame()
df_checker = df_map.loc[df_map['Weeknumber']==latestWeek ]
#print(df_checker.info())

df_checker = df_checker[(df_checker['UCL_check']==0) | (df_checker['LCL_check']==0)]
#df_checker = df_checker.reset_index(drop=True)

print(df_checker.head())
print(len(df_checker))
#df_checker.set_index(np.arange(len(df_checker)))

# Final data that is to sent over mail(s)
DataWithSenderList = pd.merge(df_checker, receivers, how='left', left_on = 'Key', right_on = 'Key')
#DataWithSenderList.to_csv('check5.csv')



##------------- Sending the mails  ------------------##


if DataWithSenderList.empty:
    print('All sales figure are withing the range for the week: ' + latestWeek)
else:
    
    mailList = list(DataWithSenderList['Mail id'].unique())
    today = date.today()
    
    # exchange Sign In
    exchange_sender = df.loc[0,'sender']
    exchange_passwd = df.loc[0,'password_s']
        
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(exchange_sender, exchange_passwd)
    
    for receiver in mailList:
        TO = receiver
        SUBJECT = 'Sales Trigger for ' + str(today)
        
        TEXT = ''
        DataToSend = DataWithSenderList[DataWithSenderList['Mail id']==receiver]
        DataToSend = DataToSend.reset_index(drop=True)
        for i in range(len(DataToSend)):
            if DataToSend.loc[i,'UCL_check']==0:
                TEXT = TEXT + 'Last week sales dollar value is $' + '%.2f'%DataToSend.loc[i, 'Sum of Sales'] + ' for '+str(DataToSend.loc[i,'Key']) + ' which exceeds from Upper Threshold Level of $'+'%.2f'%DataToSend.loc[i,'UCLmean+sigma1'] + ' \r\r\n'
            else:
                TEXT = TEXT + 'Last week sales dollar value is $' + '%.2f'%DataToSend.loc[i, 'Sum of Sales'] + ' for '+str(DataToSend.loc[i,'Key']) + ' which falls below from Lower Threshold Level of $'+'%.2f'%DataToSend.loc[i,'LCLmean-sigma1'] + ' \r\r\n'
        print(TEXT)
        
        BODY = '\r\n'.join(['To: %s' % TO,
                            'From: %s' % exchange_sender,
                            'Subject: %s' % SUBJECT,
                            '', TEXT])
        
        try:
            server.sendmail(exchange_sender, receiver, BODY)
            print ('email sent to ' + receiver)
        except:
            print ('error sending mail to '+receiver)
        
    server.quit()
