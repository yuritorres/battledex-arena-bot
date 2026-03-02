from shop import buscar_item
from financeiro.coins_db import get_coins, remove_coins
from inventario import adicionar_ao_inventario

# Função para comprar um item da loja
def comprar_item(nome_usuario, item_id):
    """
    Tenta comprar o item com id_item=item_id para o usuário nome_usuario.
    Retorna (True, mensagem) se a compra for realizada, ou (False, mensagem) se não for possível.
    """
    item = buscar_item(item_id)
    if not item:
        return False, f"❌ Item '{item_id}' não encontrado na loja."
    _, id_item, nome, preco, imagem = item
    saldo = get_coins(nome_usuario)
    if saldo < preco:
        return False, f"Saldo insuficiente. Você tem apenas {saldo} moedas e o item custa {preco}."
    remove_coins(nome_usuario, preco)
    adicionar_ao_inventario(nome_usuario, id_item, 1)
    return True, f"✅ Você comprou *{nome}* por {preco} moedas! O item foi adicionado ao seu inventário."
