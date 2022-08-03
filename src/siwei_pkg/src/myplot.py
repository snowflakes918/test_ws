import pandas as pd
import matplotlib.pyplot as plt

df_vial = pd.read_csv('./data/vial_robot_pose_data.csv')
df_tag = pd.read_csv('./data/tag_pose_data.csv')
df_home_tag = pd.read_csv('./data/home_tag_pose_data.csv')

print(df_vial)

plt.scatter(df_vial.x, df_vial.y)
plt.show()