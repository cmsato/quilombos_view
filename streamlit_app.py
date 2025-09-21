import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Set page config
st.set_page_config(
    page_title="Mapa das Comunidades Quilombolas do Brasil",
    page_icon="🗺️",
    layout="wide"
)

# Title and description
st.title("🗺️ Mapa das Comunidades Quilombolas do Brasil")
st.markdown("Selecione as comunidades quilombolas para visualizar no mapa")

# Color mapping for biomes
BIOME_COLORS = {
    'Amazônia': 'green',
    'Caatinga': 'yellow', 
    'Cerrado': 'orange',
    'Mata Atlântica': 'purple',
    'Pampa': 'blue'
}

@st.cache_data
def load_data():
    """Load the CSV data"""
    try:
        df = pd.read_csv('selecionados.csv')
        return df
    except FileNotFoundError:
        st.error("❌ Arquivo 'selecionados.csv' não encontrado. Por favor, coloque o arquivo na mesma pasta do aplicativo.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Erro ao carregar o arquivo: {e}")
        st.stop()

@st.cache_data
def load_preselected():
    """Load pre-selected communities CSV"""
    try:
        preselected_df = pd.read_csv('pre_selecionados.csv')
        # Assuming the CSV has a column with community names - adjust column name as needed
        if 'Nome' in preselected_df.columns:
            return preselected_df['Nome'].tolist()
        elif 'nome' in preselected_df.columns:
            return preselected_df['nome'].tolist()
        else:
            # If column name is different, take the first column
            return preselected_df.iloc[:, 0].tolist()
    except FileNotFoundError:
        st.warning("⚠️ Arquivo 'pre_selecionados.csv' não encontrado. Nenhuma comunidade será pré-selecionada.")
        return []
    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar pré-selecionados: {e}")
        return []

# Load data
df = load_data()
preselected_communities = load_preselected()

# Show info about pre-selected communities
if preselected_communities:
    st.sidebar.success(f"✅ {len(preselected_communities)} comunidades pré-selecionadas carregadas!")
    
    # Option to clear pre-selection
    if st.sidebar.button("🔄 Limpar pré-seleção"):
        preselected_communities = []
        st.rerun()

# Sidebar for community selection by biome
st.sidebar.header("🌿 Seleção por Bioma")

selected_communities = []

# Group communities by biome and create selection for each
for biome in sorted(df['Bioma'].unique()):
    communities_in_biome = df[df['Bioma'] == biome]['Nome'].tolist()
    
    # Color indicator for biome
    color_emoji = {
        'Amazônia': '🟢', 
        'Caatinga': '🟡', 
        'Cerrado': '🟠', 
        'Mata Atlântica': '🟣', 
        'Pampa': '🔵'
    }.get(biome, '⚫')
    
    st.sidebar.subheader(f"{color_emoji} {biome} ({len(communities_in_biome)} comunidades)")
    
    # Multiselect for each biome with pre-selected communities
    preselected_in_biome = [comm for comm in preselected_communities if comm in communities_in_biome]
    
    selected_in_biome = st.sidebar.multiselect(
        f"Selecionar em {biome}:",
        options=communities_in_biome,
        default=preselected_in_biome,
        key=f"biome_{biome}",
        label_visibility="collapsed"
    )
    
    selected_communities.extend(selected_in_biome)

# Filter dataframe to selected communities
final_df = df[df['Nome'].isin(selected_communities)]

# Main map
if len(final_df) > 0:
    # Create the map
    brazil_center = [-14.235004, -51.92528]
    m = folium.Map(
        location=brazil_center,
        zoom_start=4,
        tiles='OpenStreetMap'
    )
    
    # Add markers for selected communities
    for idx, row in final_df.iterrows():
        # Get color based on biome
        color = BIOME_COLORS.get(row['Bioma'], 'gray')
        
        # Create popup text with the requested information
        popup_text = f"""
        <div style="font-family: Arial; width: 250px;">
            <h4 style="color: #2E4057; margin-bottom: 10px;">🏘️ {row['Nome']}</h4>
            <hr style="margin: 5px 0;">
            <p><strong>🌿 Bioma:</strong> {row['Bioma']}</p>
            <p><strong>⚠️ Intempérie:</strong> {row['Intempérie']}</p>
            <p><strong>👥 População Quilombola:</strong> {row['População Quilombola']}</p>
            <p><strong>📍 Macrorregião:</strong> {row['Macrorregião']}</p>
        </div>
        """
        
        # Add marker
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=8,
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=f"{row['Nome'][:40]}..." if len(row['Nome']) > 40 else row['Nome'],
            color='black',
            weight=2,
            fillColor=color,
            fillOpacity=0.8
        ).add_to(m)
    
    # Display the map
    st.subheader(f"📍 {len(final_df)} comunidades selecionadas")
    map_data = st_folium(m, width=None, height=600)
    
else:
    st.info("⚠️ Nenhuma comunidade selecionada. Use a barra lateral para escolher as comunidades por bioma.")
    
    # Show empty map of Brazil
    brazil_center = [-14.235004, -51.92528]
    m = folium.Map(
        location=brazil_center,
        zoom_start=4,
        tiles='OpenStreetMap'
    )
    st_folium(m, width=None, height=600)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666666; padding: 10px;'>
        📍 Aplicativo para visualização das Comunidades Quilombolas do Brasil
    </div>
    """, 
    unsafe_allow_html=True
)