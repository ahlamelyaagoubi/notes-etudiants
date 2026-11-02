\# Exigences de sécurité de l'application des notes

|Exigence : « Le système doit… »|Vérification|Étape du SDLC|Test|
|-|-|-|-|
| Résister aux tentatives d'injection SQL lors de la recherche d'un étudiant|La recherche avec une entrée malveillante ne doit retourner aucune note non autorisée|Implémentation|S1|
|Refuser une modification sans authentification|<br />Réponse HTTP 401|Implémentation|S2|
|Refuser à un étudiant de modifier une note.|Réponse HTTP 403|Implémentation|S3|
|Autoriser un enseignant à modifier uniquement les notes de son module.|Réponse HTTP 403 si le module est différent|Implémentation|S4|
|Accepter uniquement une note numérique comprise entre 0 et 20.|Réponse HTTP 400 si la note est invalide|Implémentation|S5|
|Permettre à l'enseignant autorisé de modifier une note.|Réponse HTTP 200|Implémentation|S6|
|Ne pas afficher de détails techniques en cas d'erreur serveur.|Réponse sans détails techniques|Implémentation|S7|



