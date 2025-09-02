import streamlit as st

def per_product_quantity_vizualization(df):
    product_quantity_vizualization = df.set_index("Producto")["Cantidad"]
    return st.bar_chart(product_quantity_vizualization)

def per_product_brand_vizualization(df):
    product_brand_vizualization = df.set_index("Marca")["Cantidad"]
    return st.bar_chart(product_brand_vizualization, x_label="Marca", y_label="Cantidad")

def per_product_price_vizualization(df):
    product_price_vizualization = df.set_index("Precio")["Cantidad"]
    return st.bar_chart(product_price_vizualization, x_label="Precio", y_label="Cantidad")
