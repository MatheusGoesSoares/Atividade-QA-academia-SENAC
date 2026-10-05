from flask import Flask, request, jsonify, render_template
from sistema_academia import SistemaAcademia

app = Flask(__name__)
sistema = SistemaAcademia()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/reset", methods=["POST"])
def reset():
    sistema.resetar()
    return jsonify({"sucesso": True, "mensagem": "Sistema reiniciado"})


@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    data = request.get_json()
    try:
        membro = sistema.cadastrar_membro(
            data["nome"], data["cpf"], data["idade"], data["plano"]
        )
        return jsonify({
            "sucesso": True,
            "mensagem": f"Membro {membro.nome} cadastrado com sucesso",
            "dados": membro.to_dict(),
        })
    except (ValueError, KeyError, TypeError) as e:
        return jsonify({"sucesso": False, "mensagem": str(e)}), 400


@app.route("/checkin", methods=["POST"])
def checkin():
    data = request.get_json()
    try:
        sistema.fazer_checkin(data["cpf"])
        return jsonify({"sucesso": True, "mensagem": "Check-in realizado com sucesso"})
    except (ValueError, KeyError) as e:
        return jsonify({"sucesso": False, "mensagem": str(e)}), 400


@app.route("/cancelar", methods=["POST"])
def cancelar():
    data = request.get_json()
    try:
        sistema.cancelar_matricula(data["cpf"])
        return jsonify({"sucesso": True, "mensagem": "Matrícula cancelada com sucesso"})
    except (ValueError, KeyError) as e:
        return jsonify({"sucesso": False, "mensagem": str(e)}), 400


@app.route("/renovar", methods=["POST"])
def renovar():
    data = request.get_json()
    try:
        membro = sistema.renovar_plano(data["cpf"], data["plano"])
        return jsonify({
            "sucesso": True,
            "mensagem": f"Plano renovado para {membro.plano} com sucesso",
            "dados": membro.to_dict(),
        })
    except (ValueError, KeyError) as e:
        return jsonify({"sucesso": False, "mensagem": str(e)}), 400


@app.route("/consultar/<cpf>", methods=["GET"])
def consultar(cpf):
    try:
        membro = sistema.consultar_membro(cpf)
        return jsonify({"sucesso": True, "dados": membro.to_dict()})
    except ValueError as e:
        return jsonify({"sucesso": False, "mensagem": str(e)}), 404


@app.route("/membros", methods=["GET"])
def listar():
    return jsonify({"sucesso": True, "membros": sistema.listar_membros()})


if __name__ == "__main__":
    app.run(debug=False, port=5000, use_reloader=False)
