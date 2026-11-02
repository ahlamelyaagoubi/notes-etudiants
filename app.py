import os
import sqlite3
from flask import Flask, jsonify, request
from auth import utilisateur_connecte

app = Flask(__name__)
DB = "notes.db"


def init_db():
    with sqlite3.connect(DB) as con:
        con.execute(
            "CREATE TABLE IF NOT EXISTS notes "
            "(id INTEGER PRIMARY KEY, etudiant TEXT, module TEXT, note REAL)"
        )
        if con.execute("SELECT COUNT(*) FROM notes").fetchone()[0] == 0:
            con.executemany(
                "INSERT INTO notes (etudiant, module, note) VALUES (?, ?, ?)",
                [("Amina", "DevSecOps", 15.5), ("Youssef", "DevSecOps", 12.0)],
            )


init_db()


@app.route("/")
def accueil():
    return (
        "<!DOCTYPE html><html lang='fr'><head><meta charset='utf-8'>"
        "<title>Notes des etudiants</title></head><body>"
        "<h1>Consultation des notes</h1>"
        "<p><a href='/notes'>Voir les notes</a></p></body></html>"
    )


@app.route("/health")
def health():
    return jsonify(status="ok", version="1.0")


@app.route("/notes")
def lister_notes():
    etudiant = request.args.get("etudiant", "")
    with sqlite3.connect(DB) as con:
        rows = con.execute(
            "SELECT id, etudiant, module, note FROM notes WHERE etudiant LIKE ?",
            (f"%{etudiant}%",),
        ).fetchall()
    return jsonify(
        [{"id": r[0], "etudiant": r[1], "module": r[2], "note": r[3]} for r in rows]
    )

# Modification sécurisée d'une note par l'enseignant
@app.route("/notes/<note_id>", methods=["PUT"])
def modifier_note(note_id):
    utilisateur = utilisateur_connecte()

    # S2 : vérifier l'authentification
    if utilisateur is None:
        return jsonify(erreur="Authentification requise"), 401

    # S3 : vérifier le rôle
    if utilisateur.get("role") != "enseignant":
        return jsonify(erreur="Accès interdit"), 403

    # Récupérer et valider la nouvelle note
    donnees = request.get_json(silent=True) or {}
    note = donnees.get("note")

    # S5 : vérifier que la note est numérique et comprise entre 0 et 20
    if (
        isinstance(note, bool)
        or not isinstance(note, (int, float))
        or not 0 <= note <= 20
    ):
        return jsonify(erreur="Note invalide"), 400

    con = None
    try:
        con = sqlite3.connect(DB)

        # Vérifier le module de la note
        resultat = con.execute(
            "SELECT module FROM notes WHERE id = ?",
            (note_id,)
        ).fetchone()

        if resultat is None:
            return jsonify(erreur="Note introuvable"), 404

        # S4 : vérifier que l'enseignant est autorisé pour ce module
        if utilisateur.get("module") != resultat[0]:
            return jsonify(erreur="Accès interdit"), 403

        # S1 : utiliser une requête SQL paramétrée
        con.execute(
            "UPDATE notes SET note = ? WHERE id = ?",
            (note, note_id)
        )
        con.commit()

        return jsonify(status="ok"), 200

    except Exception:
        # S7 : ne pas divulguer les détails techniques
        return jsonify(erreur="Une erreur interne est survenue"), 500

    finally:
        if con is not None:
            con.close()
if __name__ == "__main__":
    app.run(host=os.environ.get("APP_HOST", "127.0.0.1"), port=5000)