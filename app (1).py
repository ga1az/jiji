from flask import Flask,request,jsonify
from flask_pymongo import PyMongo,MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from bson.json_util import dumps




app = Flask(__name__)
MONGO_URI="mongodb+srv://cris123:kiki12345@cluster0.bcpj8iu.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db =  client.products



#funciona
@app.route('/productos', methods=['POST'])
def crear_producto():
    nombre = request.json['nombre']
    descripcion = request.json['descripcion']
    categoria = request.json['categoria']
    precio = request.json['precio']
    stock = request.json['stock']
    
    result = db.productos.insert_one({
        'nombre': nombre,
        'descripcion': descripcion,
        'categoria': categoria,
        'precio': precio,
        'stock': stock
    })
    producto_id = result.inserted_id
    producto = db.productos.find_one({'_id': producto_id})
    producto['_id'] = str(producto['_id'])  

    return jsonify({'mensaje': 'Producto creado correctamente', 'producto': producto})
    
#funciona
@app.route('/productos/<id>', methods=['PUT'])
def actualizar_producto(id):
    datos_actualizados = request.json.copy()
    if '_id' in datos_actualizados:
        del datos_actualizados['_id']  # Excluir el campo _id de la actualización
    db.productos.update_one({'_id': ObjectId(id)}, {'$set': datos_actualizados})
    producto = db.productos.find_one({'_id': ObjectId(id)})
    producto['_id'] = str(producto['_id'])  # Convertir ObjectId a cadena de texto

    return dumps({'mensaje': 'Producto actualizado correctamente', 'producto': producto}), 200, {'Content-Type': 'application/json'}

#funciona
@app.route('/productos', methods=['GET'])
def listar_productos():
    productos = list(db.productos.find())
    productos_serializados = []
    for producto in productos:
        producto['_id'] = str(producto['_id'])  
        productos_serializados.append(producto)

    return jsonify({'productos': productos_serializados})

#funciona
@app.route('/productos/<id>/stock', methods=['PUT'])
def actualizar_stock(id):
    stock = request.json['stock']

    db.productos.update_one({'_id': ObjectId(id)}, {'$set': {'stock': stock}})
    producto_actualizado = db.productos.find_one({'_id': ObjectId(id)})
    producto_actualizado['_id'] = str(producto_actualizado['_id'])

    return dumps({'mensaje': 'Stock actualizado correctamente', 'producto': producto_actualizado}), 200, {'Content-Type': 'application/json'}
#funciona
@app.route('/productos/<id>', methods=['DELETE'])
def eliminar_producto(id):
    db.productos.delete_one({'_id': ObjectId(id)})
    return jsonify({'mensaje': 'Producto eliminado correctamente'})



@app.route('/pedidos', methods=['POST'])
def generar_pedido():
    productos = request.json['productos']
    total = 0
    for producto in productos:
        producto_id = producto['producto_id']
        cantidad = producto['cantidad']
        producto_db = db.productos.find_one({'_id': ObjectId(producto_id)})
        if producto_db['stock'] < cantidad:
            return jsonify({'mensaje': f'No hay suficiente stock para el producto {producto_db["nombre"]}'})
        total += producto_db['precio'] * cantidad
        db.pedidos.update_one(
            {'_id': ObjectId(producto_id)},
            {'$inc': {'stock': -cantidad}}
        )
    pedido = {
        'productos': productos,
        'total': total
    }
    db.pedidos.insert_one(pedido)  
    pedido['_id'] = str(pedido['_id'])  
    return jsonify({'mensaje': 'Pedido generado correctamente', 'pedido': pedido})


if __name__ == "__main__":
    app.run(debug=True)
