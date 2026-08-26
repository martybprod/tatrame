# Images des 56 arcanes mineurs

Rider-Waite-Smith (1909) — Pamela Colman Smith († 1951) & A. E. Waite († 1942),
domaine public en UE depuis 2022. Source : projet `TAROT` (jeu complet JPG/PNG),
copiées et renommées ici selon la convention Align.

## Convention de nommage

`{suit}_{rang}.jpg`

- `suit` ∈ `batons`, `coupes`, `epees`, `deniers`
- `rang` ∈ `as`, `2`..`10`, `valet`, `cavalier`, `reine`, `roi`

Exemples : `coupes_as.jpg`, `deniers_7.jpg`, `epees_reine.jpg`.

Ces 56 clés sont définies dans `moteur/mineurs.py` (`SUIT_NOM`, `RANGS`) —
c'est la source de vérité. Le front (`urlCarteMineur()` dans
`templates/index.html`) construit l'URL par cette même convention, avec un
repli `onerror` sur `/static/cartes/dos.jpg` si un fichier venait à manquer.

`tests/test_mineurs.py::test_images_des_56_mineurs_presentes` vérifie que
les 56 fichiers sont bien là.
