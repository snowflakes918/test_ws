import pandas as pd
import matplotlib.pyplot as plt

df_vial = pd.read_csv('./data/vial_robot_pose_data.csv')
df_tag = pd.read_csv('./data/tag_pose_data.csv')
df_home_tag = pd.read_csv('./data/home_tag_pose_data.csv')


# plt.scatter(range(10), df_vial.x)
# plt.savefig('./picture/vial_pose_x.png')
# plt.show()

# plt.scatter(range(10), df_vial.y)
# plt.savefig('./picture/vial_pose_y.png')
# plt.show()

# plt.scatter(range(10), df_vial.z)
# plt.savefig('./picture/vial_pose_z.png')
# plt.show()

# plt.scatter(range(10), df_vial.rx)
# plt.savefig('./picture/vial_pose_rx.png')
# plt.show()

# plt.scatter(range(10), df_vial.ry)
# plt.savefig('./picture/vial_pose_ry.png')
# plt.show()

# plt.scatter(range(10), df_vial.rz)
# plt.savefig('./picture/vial_pose_rz.png')
# plt.show()

vial_std = [df_vial.std().x, df_vial.std().y, df_vial.std().z, df_vial.std().rx, df_vial.std().ry, df_vial.std().rz]

y_axis = [1, 1, 1, 1, 1, 1]
plt.errorbar(df_vial.columns, y_axis, yerr=vial_std, fmt = 'o',color = 'orange', 
            ecolor = 'lightgreen', elinewidth = 5, capsize=10)
plt.show()
