#!/usr/bin/env python
# coding: utf-8

# # Введение
# 
# Кратко опишем наши данные: они представляют собой подборку демографической статистики с портала открытых данных Правительства Москвы + данные о численности населении Москвы от Росстата.
# - ID - технический номер строки
# - Year - год наблюдений
# - Month - месяц наблюдений
# - StateRegistrationOfBirth - число зарегистрированных рождений
# - NumberOfBirthCertificatesForBoys - число выданных свидетельств о рождении мальчиков
# - NumberOfBirthCertificatesForGirls - число выданных свидетельств о рождении девочек
# - StateRegistrationOfDeath - число зарегистрированных смертей
# - StateRegistrationOfMarriage - число зарегистрированных браков
# - StateRegistrationOfDivorce - число зарегистрированных разводов
# - StateRegistrationOfPaternityExamination - число зарегистрированных тестов на отцовство
# - StateRegistrationOfAdoption - число зарегистрированных усыновлений/удочерений
# - StateRegistrationOfNameChange - число зарегистрированных смен имени/фамилии
# - TotalPopulationThisYear - общая численность населения Москвы по годам

# # Предобработка данных
# 
# Импортируем необходимые библиотеки, считываем сам файл и смотрим на получившийся датасет.

# In[1]:


import numpy as np
import pandas as pd

df = pd.read_csv('moscow_stats.csv')
df.head()


# Всё считалось нормально. Теперь посмотрим, везде ли стоят подходящие типы данных.

# In[2]:


df.info() 


# Отлично, ничего поправлять не надо. Теперь проверим каждую колонку на пропуски.

# In[3]:


df.isnull().sum()


# И даже пропусков нет - какой замечательный датасет! А что там с выбросами?
# 
# Если бы у нас были пропуски, например, в StateRegistrationOfBirth (общее число рождений), то мы бы поступили таким образом: заполнили бы их техническим значением с помощью кода df.fillna(0, inplace=True)

# In[4]:


# транспонируем таблицу, чтобы потом можно было создать новый столец с интерквартильным размахом
df_stat = df[['StateRegistrationOfBirth', 'NumberOfBirthCertificatesForBoys', 'NumberOfBirthCertificatesForGirls', 'StateRegistrationOfDeath', 'StateRegistrationOfMarriage', 'StateRegistrationOfDivorce', 'StateRegistrationOfPaternityExamination', 'StateRegistrationOfAdoption', 'StateRegistrationOfNameChange', 'TotalPopulationThisYear']].describe().T

# столбец с интерквартильным размахом
df_stat['iqr'] = df_stat['75%'] - df_stat['25%']

# определяем нижнюю и верхнюю границу допустимых значений
df_stat['lower_bound'] = df_stat['25%'] - 1.5 * df_stat['iqr']
df_stat['upper_bound'] = df_stat['75%'] + 1.5 * df_stat['iqr']

# создаём дополнительный признак, который показывает, есть ли выбросы по каждой из границ
df_stat['any_outlier_min'] = np.where(df_stat['lower_bound'] - df_stat['min'] > 0, 'yes', 'no')
df_stat['any_outlier_max'] = np.where(df_stat['max'] - df_stat['upper_bound'] > 0, 'yes', 'no')

df_stat


# Так, выбросов много, где-то они даже есть с обеих сторон. Для простоты восприятия давайте их визуализируем

# In[5]:


import matplotlib.pyplot as plt 
get_ipython().run_line_magic('matplotlib', 'inline')

fig, ax = plt.subplots(2, 5, figsize=(14,9))
ax[0][0].scatter(df.ID, df.StateRegistrationOfBirth)
ax[0][1].scatter(df.ID, df.NumberOfBirthCertificatesForBoys)
ax[0][2].scatter(df.ID, df.NumberOfBirthCertificatesForGirls)
ax[0][3].scatter(df.ID, df.StateRegistrationOfDeath)
ax[0][4].scatter(df.ID, df.StateRegistrationOfMarriage)
ax[1][0].scatter(df.ID, df.StateRegistrationOfDivorce)
ax[1][1].scatter(df.ID, df.StateRegistrationOfPaternityExamination)
ax[1][2].scatter(df.ID, df.StateRegistrationOfAdoption)
ax[1][3].scatter(df.ID, df.StateRegistrationOfNameChange)
ax[1][4].scatter(df.ID, df.TotalPopulationThisYear);


# Посмотрели - и хватит, давайте удалим выбросы, чтобы они не портили статистику.
# 
# Из того, что мы видим, выбросы надо удалять везде, кроме StateRegistrationOfMarriage и TotalPopulationThisYear. Причём в StateRegistrationOfDeath надо удалять выбросы сверху, в StateRegistrationOfAdoption - и сверху, и снизу, а во всех остальных - снизу.

# In[6]:


df.drop(df[df.StateRegistrationOfBirth < 8.649875e+03].index, inplace=True)
df.drop(df[df.NumberOfBirthCertificatesForBoys < 4.472125e+03].index, inplace=True) 
df.drop(df[df.NumberOfBirthCertificatesForGirls < 4.175000e+03].index, inplace=True)
df.drop(df[df.StateRegistrationOfDeath > 1.146538e+04].index, inplace=True)
df.drop(df[df.StateRegistrationOfDivorce < 2.811625e+03].index, inplace=True)
df.drop(df[df.StateRegistrationOfPaternityExamination < 1.038875e+03].index, inplace=True)
df.drop(df[df.StateRegistrationOfAdoption < 2.887500e+01].index, inplace=True)
df.drop(df[df.StateRegistrationOfAdoption > 1.378750e+02].index, inplace=True)
df.drop(df[df.StateRegistrationOfNameChange < 4.278750e+02].index, inplace=True)


# # Описательные статистики

# При помощи метода describe мы смотрим описательные статистики для количественных переменных. 

# In[7]:


df.describe()


# 1. Можно отметить интересный факт, что изначально мальчиков рождается больше, чем девочек. В среднем это 5821 мальчик на 5461 девочку, но при этом с течением жизни это соотношение меняется в пользу девочек. 
# 
# 2. Кроме того, интересным представляется факт, что количество заключенных браков в среднем чуть больше, чем в 2 раза превышает число разводов. Это дает нам надежду на то, что любовь победит 🫶🏻
# 
# 3. Средняя смертность ниже, чем средняя рождаемость, что говорит о положительном естественном приросте населения.

# In[8]:


df.groupby('Month')['StateRegistrationOfBirth'].sum().sort_values(ascending=False)


# Самый большой месяц по рождаемости – октябрь. Мы проанализировали, сделали необходимые расчеты и пришли к выводу, что потенциальный месяц зачатия – февраль. Мы выделили 3 причины для такого явления:
# 
# 1. Все хотят детей Весов 
# 2. Февраль – время холодов в Москве, когда они уже всем надоели и все насмотрелись на снег, поэтому предпочитают сидеть дома и согреваться теплом друг друга
# 3. Исполнение супружеского долга является популярным подарком на 23 февраля

# # Построение модели машинного обучения

# Мы решили построить модель линейной регрессии, чтобы проверить влияние количества заключенных браков на число рожденных детей. Таргетом будет являться StateRegistrationOfBirth, а признаком будет переменная StateRegistrationOfMarriage. 

# In[9]:


import statsmodels.formula.api as smf

# создаём модель по заданной формуле и обучаем ее на data при помощи метода .fit()
lm = smf.ols(formula='StateRegistrationOfBirth ~ StateRegistrationOfMarriage', data=df).fit()

# выведем полученные коэффициенты модели
lm.params


# In[ ]:


#итоговая формула для линейной регрессии 

StateRegistrationOfBirth = 9802.308981 + 0.190475*StateRegistrationOfMarriage


# Посмотрим на p-value признака, чтобы определить, нужно ли нам его учитывать

# In[10]:


lm.summary()


# P-value 0, поэтому признак является репрезентативным, мы можем делать прогнозы, основываясь на нем.

# ### Интерпретация коэффициентов модели

# Как мы интерпретируем StateRegistrationOfMarriage коэффициент (𝛽1)?
# 
# Дополнительные 1000 браков увеличивают число зарегистрированных рождений детей на 190.
# 
# Обратим внимание, что если бы увеличение браков приводило к снижению рождаемости, то  𝛽1 был бы отрицательным.

# In[11]:


#Сделаем прогноз 

k = 9802.308981 + 0.190475*69
print(f'При увеличении числа браков на 69 число рождений становится равным {round(k)}')


# ## Построение модели множественной регрессии

# Мы решили построить модель множественной линейной регрессии, чтобы посмотреть влияние количества разводов и количества усыновлений на количество рожденных детей. Таргетом будет являться StateRegistrationOfBirth, а признаками будут являться переменные StateRegistrationOfDivorce, StateRegistrationOfAdoption. 

# In[15]:


# создаём модель по заданной формуле и обучаем ее на data при помощи метода .fit()
lm = smf.ols(formula='StateRegistrationOfBirth ~ StateRegistrationOfDivorce + StateRegistrationOfAdoption', data=df).fit()

# выведем полученные коэффициенты модели
lm.params


# In[ ]:


#формула множественной линейной регрессии

StateRegistrationOfBirth = 7550.006123 + 0.981285*StateRegistrationOfDivorce + 0.786954*StateRegistrationOfAdoption


# In[16]:


lm.summary()


# Смотрим на p-value признаков. В случае с разводами p-value 0, поэтому мы можем использовать этот признак для прогнозирования, а количество усыновлений не является таковым, потому что у него p-value высокий, соответственно, мы не можем использовать этот признак, потому что высока вероятность ошибки.

# R-квадрат в данной модели обучения меньше, чем в предыдущей модели линейной регресии, значит, эта модель менее репрезентативна, чем предыдущая.

# In[23]:


#Сделаем прогноз по итоговой формуле

g = 7550.006123 + 0.981285*100 + 0.786954*100


# Интерпретация результатов такова, что в настоящее время снижается ценность брака в рамках рождения детей, потому что увеличение числа разводов на 100 приводит к увеличению числа рождений на 98 ребенка.

# # the best ever визуализация

# In[26]:


fig, ax = plt.subplots(figsize=(16,9))
ax.scatter(df['Month'], df['StateRegistrationOfDivorce'])
ax.set_xlabel('Месяцы', fontsize=12)
ax.set_ylabel('Количество разводов', fontsize=12);


# **Вывод**: Если смотреть на график, то зависимости между месяцем и числом разводов нет

# In[29]:


fig, ax = plt.subplots(figsize=(16,9))
plt.bar(df['Year'], df['NumberOfBirthCertificatesForGirls'], color = 'pink')
ax.set_xlabel('Годы', fontsize=12)
ax.set_ylabel('Количество рожденных девочек', fontsize=12);


# **Вывод**: Начиная с 2010 года и до 2015 наблюдался рост рождаемости девочек, а после начался спад. Некое улучшение ситуации произошло в 2019 году. В 2020 году учитывались только январь и февраль, но уровень рождаемости девочек уже оказался равен примерно 3/4 от общей рождаемости девочек за 12 месяцев 2019 года. 

# In[30]:


df2015 = df[df['Year'] == 2015]
mylabels = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
y = df2015.groupby('Month')['StateRegistrationOfBirth'].sum()

fig, ax = plt.subplots(figsize=(10,10))
plt.pie(y, labels=mylabels, autopct ='%1.1f%%')
plt.legend(title='Months:')
plt.title('Количество рождений по месяцам в процентах (на примере 2015 года)')
plt.show()


# **Вывод**: больше всего девочек рождается в июне. Второе место делят ноябрь и июль.
