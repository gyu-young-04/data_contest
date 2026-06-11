import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
# PCA - 변수들을 조합하여 데이터의 특징을 가장 잘 설명하는 
# 소수의 주성분으로 압축 (여러 데이터들을 2차원으로 드러내기위함)


# 1. 가상의 데이터셋 생성 (배달 건수, 소득, 사고율, 지역 밀도)
np.random.seed(42)
data_size = 100
regions = [f'Region_{i}' for i in range(data_size)]
delivery_counts = np.random.randint(1000, 5000, data_size)
income_avg = np.random.randint(200, 500, data_size)
accident_rate = (delivery_counts * 0.001) + np.random.normal(0, 0.5, data_size)
population_density = np.random.randint(500, 2000, data_size)


df = pd.DataFrame({
    'Region': regions,
    'Delivery_Count': delivery_counts,
    'Income_Avg': income_avg,
    'Accident_Rate': accident_rate,
    'Pop_Density': population_density
})

# 2. 데이터 표준화 (Standardization) 
features = ['Delivery_Count', 'Income_Avg', 'Accident_Rate', 'Pop_Density']
scaler = StandardScaler()
df_scaled = scaler.fit_transform(df[features])

# 3. K-평균 군집화 (Clustering) 
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(df_scaled)

# 4. 시각화를 위한 차원 축소 (PCA) 
pca = PCA(n_components=2)
pca_result = pca.fit_transform(df_scaled)
df['PCA1'] = pca_result[:, 0]
df['PCA2'] = pca_result[:, 1]

# 1. 군집화 결과 시각화 (첫 번째 그래프)
plt.figure(figsize=(8, 6)) # 새 도화지 선언
sns.scatterplot(x='PCA1', y='PCA2', hue='Cluster', data=df, palette='viridis', s=100)
plt.title('Region Clustering (PCA Analysis)')
plt.savefig('clustering_result.png') # 개별 저장
plt.show() # 출력

# 2. 배달 건수 vs 사고율 시각화 (두 번째 그래프)
plt.figure(figsize=(8, 6)) # 새 도화지 선언
sns.regplot(x='Delivery_Count', y='Accident_Rate', data=df, scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
plt.title('Delivery Count vs Accident Rate')
plt.savefig('regression_result.png') # 개별 저장
plt.show() # 출력

print(df.head())