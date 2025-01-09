from PIL import Image
import os

def converter_png_para_ico(caminho_arquivo_png, caminho_arquivo_ico, tamanho_ico=(256, 256)):
    try:
  
        img = Image.open(caminho_arquivo_png)
        
        img = img.resize(tamanho_ico, Image.ANTIALIAS)
        
        img.save(caminho_arquivo_ico, format="ICO")
        print(f"Arquivo convertido com sucesso: {caminho_arquivo_ico}")
    except Exception as e:
        print(f"Erro ao converter o arquivo: {e}")

if __name__ == "__main__":
  
    arquivo_png = "imagem.png"  # Substitua pelo nome do arquivo PNG
    
    # Caminho do arquivo ICO (saída)
    arquivo_ico = "imagem.ico"  # Substitua pelo nome do arquivo ICO
    
    # Tamanho desejado do ícone (opcional)
    tamanho = (256, 256)  # Altere se necessário
    
    # Verifica se o arquivo PNG existe
    if os.path.exists(arquivo_png):
        converter_png_para_ico(arquivo_png, arquivo_ico, tamanho)
    else:
        print(f"Arquivo PNG não encontrado: {arquivo_png}")
