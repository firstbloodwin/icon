import pandas as pd

# 示例 DataFrame
data = {
    'name': ['Alice', 'Alice'],
    '日期': ['今天', '昨天'],
    '微信': [120, 150],
    '抖音': [80, 60],
    '微博': [40, 30]
}
df = pd.DataFrame(data)
df = df.set_index(['name', '日期'])

# 使用unstack()方法将数据展开
df_unstacked = df.unstack()

# 重命名列，使其包含“今天”和“昨天”的标识
df_unstacked.columns = [f'{app}_{day}' for app, day in df_unstacked.columns]

# 重置索引，使name成为DataFrame的一个普通列
df_unstacked = df_unstacked.reset_index()

print(df_unstacked)

# 插入新列
import pandas as pd

# 创建一个示例DataFrame
df = pd.DataFrame({'A': [0, 1, 2, 0], 'B': [3, 4, 5, 6], 'C': [7, 8, 9, 10]})

# 指定要在其后插入新列的列名
column_to_insert_after = 'A'

# 插入新列'D'，其值根据列'A'的值来确定
df.insert(
    df.columns.get_loc(column_to_insert_after) + 1, 'D',
    [(12 if x != 0 else 26) for x in df['A']])

print(df)
