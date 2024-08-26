import requests
import json
from tqdm import tqdm

def extraindo_codigos_municipios(quantidade_municipios=184):
    url = "https://divulgacandcontas.tse.jus.br/divulga/rest/v1/eleicao/buscar/PE/2045202024/municipios"
    response_municipios = requests.get(url)
    json_res_municipios = response_municipios.json()

    codigos_municipio = [json_res_municipios['municipios'][i]['codigo'] for i in range(int(quantidade_municipios))]
    return codigos_municipio

def candidatos_por_municipio(codigo_mun):
    url = f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/listar/2024/{codigo_mun}/2045202024/11/candidatos"
    response = requests.get(url)
    data = response.json()

    info_eleitoral = data.get('unidadeEleitoral', {}).get('nome', 'Desconhecido')
    candidatos = data.get('candidatos', [])

    candidatos_info = {
        candidato['id']: {
            'nome': candidato['nomeUrna'],
            'cidade': info_eleitoral,
        }
        for candidato in candidatos
    }
    
    return candidatos_info

# --- obter candidatos por município ---
codigos_municipios = extraindo_codigos_municipios(15)
lista_candidatos = {}
for codigo_municipio in tqdm(codigos_municipios, desc="Obtendo candidatos por município"):
    lista_candidatos[codigo_municipio] = candidatos_por_municipio(codigo_mun=codigo_municipio)

# --- buscar Instagram dos candidatos e formatar a saída ---
resultados = {}

for codigo_municipio, candidatos in tqdm(lista_candidatos.items(), desc="Buscando Instagram dos candidatos"):
    resultados[codigo_municipio] = {}
    for candidato_id, info in candidatos.items():
        url = f"https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/buscar/2024/{codigo_municipio}/2045202024/candidato/{candidato_id}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            instagram_sites = [site for site in data.get('sites', []) if 'instagram.com' in site]
            instagram_url = instagram_sites[0] if instagram_sites else None
            
            resultados[codigo_municipio][candidato_id] = {
                'nome': info['nome'],
                'cidade': info['cidade'],
                'instagram': instagram_url
            }
        
        except requests.RequestException as e:
            print(f"Erro ao acessar dados do candidato {candidato_id}: {e}")
            resultados[codigo_municipio][candidato_id] = {
                'nome': info['nome'],
                'cidade': info['cidade'],
                'instagram': None
            }

# --- salvar os resultados em um arquivo JSON ---
with open('candidatos_instagram.json', 'w', encoding='utf-8') as f:
    json.dump(resultados, f, ensure_ascii=False, indent=4)

print("Arquivo JSON criado com sucesso!")
