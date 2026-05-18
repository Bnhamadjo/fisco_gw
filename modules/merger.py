import pandas as pd

def juntar_ficheiros(df1, df2):
    return pd.concat([df1, df2])

if len(dfs) >= 2:
    if st.button("🔗 Juntar ficheiros"):
        df = juntar_ficheiros(dfs[0], dfs[1])
        st.success("Ficheiros combinados!")
        st.write(df.head())