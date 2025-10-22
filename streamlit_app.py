"""
╔═══════════════════════════════════════════════════════════════╗
║          TIENDA AURELION - APLICACIÓN WEB                     ║
║          Sistema de Gestión de Inventario con Streamlit       ║
║          Sprint 1 - Introducción a la IA - IBM                ║
║                                                               ║
║          Autor: Martos Ludmila                                ║
║          DNI: 34811650                                        ║
╚═══════════════════════════════════════════════════════════════╝

Aplicación web interactiva para gestionar el inventario de la Tienda Aurelion.

Instalación de Streamlit:
    pip install streamlit

Ejecución:
    streamlit run app_streamlit.py
"""

import streamlit as st
import csv
import pandas as pd
import os
from typing import List, Dict

# Configuración de la página
st.set_page_config(
    page_title="Tienda Aurelion",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constantes
# Detectar automáticamente la ruta correcta del CSV
def obtener_ruta_csv():
    """Obtiene la ruta correcta del CSV independientemente de desde dónde se ejecute."""
    rutas_posibles = [
        "../datos/tienda_aurelion.csv",  # Ejecutando desde programas/
        "datos/tienda_aurelion.csv",      # Ejecutando desde Sprint 1/
        "Sprint 1/datos/tienda_aurelion.csv"  # Ejecutando desde raíz del repo
    ]
    for ruta in rutas_posibles:
        if os.path.exists(ruta):
            return ruta
    return "../datos/tienda_aurelion.csv"  # Por defecto

ARCHIVO_CSV = obtener_ruta_csv()
UMBRAL_STOCK_BAJO = 20

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FFD700;
        text-shadow: 2px 2px 4px #000000;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #667eea;
    }
    .stock-bajo {
        color: #ff4444;
        font-weight: bold;
    }
    .stock-ok {
        color: #00C851;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def cargar_datos() -> pd.DataFrame:
    """
    Carga los datos del archivo CSV y los convierte en DataFrame de pandas.
    """
    try:
        df = pd.read_csv(ARCHIVO_CSV, encoding='utf-8')
        # Asegurar tipos de datos correctos
        df['id'] = df['id'].astype(int)
        df['precio'] = df['precio'].astype(int)
        df['stock'] = df['stock'].astype(int)
        return df
    except FileNotFoundError:
        st.error(f"❌ No se encontró el archivo '{ARCHIVO_CSV}'")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {e}")
        return pd.DataFrame()


def guardar_datos(df: pd.DataFrame):
    """Guarda el DataFrame en el archivo CSV."""
    try:
        df.to_csv(ARCHIVO_CSV, index=False, encoding='utf-8')
        return True
    except Exception as e:
        st.error(f"❌ Error al guardar: {e}")
        return False


def mostrar_header():
    """Muestra el encabezado principal de la aplicación."""
    st.markdown(
        '<div class="main-header">⚔️ TIENDA AURELION ⚔️<br><small style="font-size:1.2rem;">Sistema de Gestión de Inventario</small></div>',
        unsafe_allow_html=True
    )


def mostrar_metricas_principales(df: pd.DataFrame):
    """Muestra las métricas principales en tarjetas."""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="📦 Total Productos",
            value=len(df)
        )
    
    with col2:
        stock_total = df['stock'].sum()
        st.metric(
            label="📊 Stock Total",
            value=f"{stock_total:,}",
            help="Unidades totales en inventario"
        )
    
    with col3:
        valor_total = (df['precio'] * df['stock']).sum()
        st.metric(
            label="💰 Valor Inventario",
            value=f"{valor_total:,}",
            help="Monedas de oro"
        )
    
    with col4:
        categorias = df['categoria'].nunique()
        st.metric(
            label="🏷️ Categorías",
            value=categorias
        )
    
    with col5:
        productos_bajo_stock = len(df[df['stock'] <= UMBRAL_STOCK_BAJO])
        st.metric(
            label="⚠️ Stock Bajo",
            value=productos_bajo_stock,
            delta=f"-{productos_bajo_stock}" if productos_bajo_stock > 0 else "OK",
            delta_color="inverse"
        )


def pagina_inicio(df: pd.DataFrame):
    """Página de inicio con resumen general."""
    st.header("📊 Panel de Control General")
    
    # Métricas principales
    mostrar_metricas_principales(df)
    
    st.markdown("---")
    
    # Dos columnas para gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Productos por Categoría")
        categoria_counts = df['categoria'].value_counts()
        st.bar_chart(categoria_counts)
        
        st.subheader("💵 Distribución de Precios")
        precio_dist = pd.cut(df['precio'], bins=[0, 500, 2000, 10000], 
                            labels=['Económico (<500)', 'Medio (500-2000)', 'Premium (>2000)'])
        st.bar_chart(precio_dist.value_counts())
    
    with col2:
        st.subheader("🏪 Productos por Proveedor")
        proveedor_counts = df['proveedor'].value_counts()
        st.bar_chart(proveedor_counts)
        
        st.subheader("💎 Top 5 Más Valiosos")
        df_valor = df.copy()
        df_valor['valor_total'] = df_valor['precio'] * df_valor['stock']
        top5 = df_valor.nlargest(5, 'valor_total')[['nombre', 'valor_total']]
        top5 = top5.set_index('nombre')
        st.bar_chart(top5)
    
    # Alerta de productos con stock bajo
    if len(df[df['stock'] <= UMBRAL_STOCK_BAJO]) > 0:
        st.markdown("---")
        st.warning("⚠️ **ALERTA: Productos con Stock Bajo**")
        productos_criticos = df[df['stock'] <= UMBRAL_STOCK_BAJO].sort_values('stock')
        st.dataframe(
            productos_criticos[['nombre', 'categoria', 'stock', 'proveedor']],
            use_container_width=True,
            hide_index=True
        )


def pagina_productos(df: pd.DataFrame):
    """Página para ver y buscar productos."""
    st.header("🔍 Explorar Productos")
    
    # Filtros en la barra lateral
    st.sidebar.subheader("🎛️ Filtros")
    
    # Filtro por categoría
    categorias = ['Todas'] + sorted(df['categoria'].unique().tolist())
    categoria_seleccionada = st.sidebar.selectbox("Categoría", categorias)
    
    # Filtro por proveedor
    proveedores = ['Todos'] + sorted(df['proveedor'].unique().tolist())
    proveedor_seleccionado = st.sidebar.selectbox("Proveedor", proveedores)
    
    # Filtro por rango de precio
    precio_min, precio_max = st.sidebar.slider(
        "Rango de Precio (monedas)",
        min_value=int(df['precio'].min()),
        max_value=int(df['precio'].max()),
        value=(int(df['precio'].min()), int(df['precio'].max()))
    )
    
    # Filtro por stock
    stock_filter = st.sidebar.radio(
        "Estado de Stock",
        ["Todos", "Stock Bajo (≤20)", "Stock Saludable (>20)"]
    )
    
    # Búsqueda por nombre
    busqueda = st.sidebar.text_input("🔎 Buscar por nombre", "")
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if categoria_seleccionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_seleccionada]
    
    if proveedor_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['proveedor'] == proveedor_seleccionado]
    
    df_filtrado = df_filtrado[
        (df_filtrado['precio'] >= precio_min) & 
        (df_filtrado['precio'] <= precio_max)
    ]
    
    if stock_filter == "Stock Bajo (≤20)":
        df_filtrado = df_filtrado[df_filtrado['stock'] <= UMBRAL_STOCK_BAJO]
    elif stock_filter == "Stock Saludable (>20)":
        df_filtrado = df_filtrado[df_filtrado['stock'] > UMBRAL_STOCK_BAJO]
    
    if busqueda:
        df_filtrado = df_filtrado[
            df_filtrado['nombre'].str.contains(busqueda, case=False, na=False)
        ]
    
    # Mostrar resultados
    st.subheader(f"📦 Resultados: {len(df_filtrado)} producto(s)")
    
    if len(df_filtrado) > 0:
        # Agregar columna de estado de stock
        df_display = df_filtrado.copy()
        df_display['Estado'] = df_display['stock'].apply(
            lambda x: '⚠️ BAJO' if x <= UMBRAL_STOCK_BAJO else '✅ OK'
        )
        
        # Mostrar tabla
        st.dataframe(
            df_display[['id', 'nombre', 'categoria', 'precio', 'stock', 'Estado', 'proveedor', 'descripcion']],
            use_container_width=True,
            hide_index=True
        )
        
        # Estadísticas de los resultados filtrados
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Stock Total", f"{df_filtrado['stock'].sum():,}")
        with col2:
            valor = (df_filtrado['precio'] * df_filtrado['stock']).sum()
            st.metric("Valor Total", f"{valor:,} 💰")
        with col3:
            precio_prom = df_filtrado['precio'].mean()
            st.metric("Precio Promedio", f"{precio_prom:.0f} 💰")
    else:
        st.info("No se encontraron productos con los filtros seleccionados.")


def pagina_estadisticas(df: pd.DataFrame):
    """Página de estadísticas y análisis."""
    st.header("📊 Estadísticas y Análisis")
    
    # Estadísticas generales
    st.subheader("📈 Estadísticas Generales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Productos", len(df))
        st.metric("Categorías Únicas", df['categoria'].nunique())
    
    with col2:
        st.metric("Stock Total", f"{df['stock'].sum():,}")
        st.metric("Stock Promedio", f"{df['stock'].mean():.1f}")
    
    with col3:
        valor_total = (df['precio'] * df['stock']).sum()
        st.metric("Valor Total", f"{valor_total:,} 💰")
        st.metric("Precio Promedio", f"{df['precio'].mean():.0f} 💰")
    
    with col4:
        st.metric("Proveedores Únicos", df['proveedor'].nunique())
        productos_bajo = len(df[df['stock'] <= UMBRAL_STOCK_BAJO])
        st.metric("Productos Stock Bajo", productos_bajo)
    
    st.markdown("---")
    
    # Análisis por categoría
    st.subheader("🏷️ Análisis por Categoría")
    
    analisis_categoria = df.groupby('categoria').agg({
        'id': 'count',
        'stock': 'sum',
        'precio': 'mean'
    }).rename(columns={
        'id': 'Cantidad Productos',
        'stock': 'Stock Total',
        'precio': 'Precio Promedio'
    })
    
    analisis_categoria['Valor Total'] = df.groupby('categoria').apply(
        lambda x: (x['precio'] * x['stock']).sum()
    )
    
    st.dataframe(
        analisis_categoria.style.format({
            'Stock Total': '{:,.0f}',
            'Precio Promedio': '{:,.0f} 💰',
            'Valor Total': '{:,.0f} 💰'
        }),
        use_container_width=True
    )
    
    st.markdown("---")
    
    # Análisis por proveedor
    st.subheader("🏪 Análisis por Proveedor")
    
    analisis_proveedor = df.groupby('proveedor').agg({
        'id': 'count',
        'stock': 'sum',
        'categoria': lambda x: x.nunique()
    }).rename(columns={
        'id': 'Productos',
        'stock': 'Stock Total',
        'categoria': 'Categorías'
    })
    
    analisis_proveedor['Valor Total'] = df.groupby('proveedor').apply(
        lambda x: (x['precio'] * x['stock']).sum()
    )
    
    analisis_proveedor = analisis_proveedor.sort_values('Productos', ascending=False)
    
    st.dataframe(
        analisis_proveedor.style.format({
            'Stock Total': '{:,.0f}',
            'Valor Total': '{:,.0f} 💰'
        }),
        use_container_width=True
    )
    
    st.markdown("---")
    
    # Productos destacados
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💎 Producto Más Caro")
        mas_caro = df.loc[df['precio'].idxmax()]
        st.info(f"""
        **{mas_caro['nombre']}**
        - Precio: {mas_caro['precio']:,} monedas
        - Categoría: {mas_caro['categoria']}
        - Stock: {mas_caro['stock']} unidades
        - Proveedor: {mas_caro['proveedor']}
        """)
    
    with col2:
        st.subheader("🎯 Producto Más Económico")
        mas_barato = df.loc[df['precio'].idxmin()]
        st.info(f"""
        **{mas_barato['nombre']}**
        - Precio: {mas_barato['precio']:,} monedas
        - Categoría: {mas_barato['categoria']}
        - Stock: {mas_barato['stock']} unidades
        - Proveedor: {mas_barato['proveedor']}
        """)


def pagina_gestionar(df: pd.DataFrame):
    """Página para gestionar el inventario (agregar/actualizar)."""
    st.header("✏️ Gestionar Inventario")
    
    tab1, tab2 = st.tabs(["➕ Agregar Producto", "🔄 Actualizar Stock"])
    
    with tab1:
        st.subheader("Agregar Nuevo Producto")
        
        with st.form("form_agregar"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("📦 Nombre del Producto *")
                categorias = sorted(df['categoria'].unique().tolist())
                categoria = st.selectbox("🏷️ Categoría", categorias)
                precio = st.number_input("💰 Precio (monedas)", min_value=1, value=100)
            
            with col2:
                stock = st.number_input("📊 Stock Inicial", min_value=0, value=10)
                proveedores = sorted(df['proveedor'].unique().tolist())
                proveedor = st.selectbox("🏪 Proveedor", proveedores)
                descripcion = st.text_area("📝 Descripción *")
            
            submitted = st.form_submit_button("✅ Agregar Producto")
            
            if submitted:
                if not nombre or not descripcion:
                    st.error("❌ El nombre y la descripción son obligatorios")
                else:
                    nuevo_id = df['id'].max() + 1
                    nuevo_producto = pd.DataFrame([{
                        'id': nuevo_id,
                        'nombre': nombre,
                        'categoria': categoria,
                        'precio': precio,
                        'stock': stock,
                        'descripcion': descripcion,
                        'proveedor': proveedor
                    }])
                    
                    df_actualizado = pd.concat([df, nuevo_producto], ignore_index=True)
                    
                    if guardar_datos(df_actualizado):
                        st.success(f"✅ Producto '{nombre}' agregado exitosamente con ID {nuevo_id}")
                        st.cache_data.clear()
                        st.rerun()
    
    with tab2:
        st.subheader("Actualizar Stock de Producto")
        
        # Selector de producto
        productos_dict = dict(zip(df['nombre'], df['id']))
        producto_seleccionado = st.selectbox(
            "Selecciona un producto",
            options=list(productos_dict.keys())
        )
        
        if producto_seleccionado:
            producto_id = productos_dict[producto_seleccionado]
            producto = df[df['id'] == producto_id].iloc[0]
            
            st.info(f"""
            **Información actual:**
            - Stock actual: **{producto['stock']}** unidades
            - Precio: {producto['precio']} monedas
            - Categoría: {producto['categoria']}
            """)
            
            with st.form("form_actualizar"):
                operacion = st.radio(
                    "Tipo de operación",
                    ["➕ Agregar stock (recepción)", "➖ Reducir stock (venta)", "🔄 Establecer nuevo stock"]
                )
                
                if operacion == "🔄 Establecer nuevo stock":
                    nuevo_stock = st.number_input("Nuevo stock", min_value=0, value=int(producto['stock']))
                else:
                    cantidad = st.number_input("Cantidad", min_value=1, value=1)
                
                submitted = st.form_submit_button("💾 Actualizar Stock")
                
                if submitted:
                    if operacion == "➕ Agregar stock (recepción)":
                        nuevo_stock = producto['stock'] + cantidad
                        mensaje = f"Se agregaron {cantidad} unidades"
                    elif operacion == "➖ Reducir stock (venta)":
                        if cantidad > producto['stock']:
                            st.error(f"❌ No hay suficiente stock. Disponible: {producto['stock']}")
                            nuevo_stock = None
                        else:
                            nuevo_stock = producto['stock'] - cantidad
                            mensaje = f"Se redujeron {cantidad} unidades"
                    else:
                        mensaje = f"Stock establecido en {nuevo_stock} unidades"
                    
                    if nuevo_stock is not None:
                        df.loc[df['id'] == producto_id, 'stock'] = nuevo_stock
                        
                        if guardar_datos(df):
                            st.success(f"✅ {mensaje}. Nuevo stock: {nuevo_stock} unidades")
                            if nuevo_stock <= UMBRAL_STOCK_BAJO:
                                st.warning("⚠️ ADVERTENCIA: Stock bajo. Considerar reabastecimiento.")
                            st.cache_data.clear()
                            st.rerun()


def main():
    """Función principal de la aplicación."""
    # Cargar datos
    df = cargar_datos()
    
    if df.empty:
        st.error("No se pudieron cargar los datos. Verifica que el archivo CSV existe.")
        return
    
    # Header
    mostrar_header()
    
    # Menú de navegación en sidebar
    st.sidebar.title("🎮 Navegación")
    pagina = st.sidebar.radio(
        "Selecciona una página:",
        ["🏠 Inicio", "🔍 Explorar Productos", "📊 Estadísticas", "✏️ Gestionar Inventario"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"""
    **📊 Resumen Rápido**
    - Total productos: **{len(df)}**
    - Stock total: **{df['stock'].sum():,}**
    - Valor inventario: **{(df['precio'] * df['stock']).sum():,} 💰**
    """)
    
    # Mostrar página seleccionada
    if pagina == "🏠 Inicio":
        pagina_inicio(df)
    elif pagina == "🔍 Explorar Productos":
        pagina_productos(df)
    elif pagina == "📊 Estadísticas":
        pagina_estadisticas(df)
    elif pagina == "✏️ Gestionar Inventario":
        pagina_gestionar(df)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        ⚔️ <b>Tienda Aurelion</b><br>
        Sistema de Gestión v1.0<br>
        IBM - Sprint 1 IA
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
