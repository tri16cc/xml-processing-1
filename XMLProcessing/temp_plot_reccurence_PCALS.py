
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
from datetime import timedelta

filepath = r""
data_pcals = pd.read_excel(filepath)

data_pcals['time_seconds'] = data_pcals['Time_Duration'].apply(lambda x: datetime.combine(date.min,  x) - datetime.min)
data_pcals['Time_Seconds_Sum'] = data_pcals['time_seconds'].apply(lambda x: x.total_seconds())
data_pcals['Recurrence'] = data_pcals['Recurrence'].map({0: 'No', 1: 'Yes'})
# plt.figure(figsize=(10,8))
sns.set_context("notebook", font_scale=1.1)
sns.set_style("ticks")
sns.set_style("whitegrid")
#%%
# sizes = [10, 60, 90, 130, 200]
# marker_size = pd.cut(data_pcals['population_total']/1000000, [0, 100, 200, 400, 600, 800], labels=sizes)
marker_size = [200, 200]
# y = data_pcals['Size']
# x = data_pcals['Time_Seconds_Sum']
# sns.lmplot('Size', 'Time_Seconds_Sum', data=data_pcals, hue='Recurrences_Yes/No', fit_reg=False, scatter_kws={'s':marker_size}, scatter=True)
sns.lmplot(x='Time_Seconds_Sum', y='Size', hue='Recurrence', data=data_pcals)
plt.title('Local Reccurence Rates PCALS')
plt.xlabel('Time Duration [seconds]')
plt.ylabel('Size[mm]')
plt.xlim((0, 500))
# plt.show()
plt.savefig('PCALS_AblationIndex_limit_plot.png')


#%% write to Excel

# filename = 'Pascale_PCALS_200patients.xlsx'
# writer = pd.ExcelWriter(filename)
# data_pcals.to_excel(writer, sheet_name='Paths', index=False, na_rep='NaN')
# writer.save()
print('success')