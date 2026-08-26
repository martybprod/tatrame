"""Extrait le texte d'un EPUB vers un .txt propre (dans l'ordre du spine).

Usage :
    ./venv/bin/python _distillation/extraire_epub.py "<chemin.epub>" "<sortie.txt>"

Bibliothèque standard uniquement (zipfile + XML + html.parser). Le .txt
produit est du texte SOUS COPYRIGHT : il vit dans _distillation/sources/
(gitignoré), jamais dans le produit ni le dépôt.
"""
import pathlib
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from html.parser import HTMLParser

NS = {"c": "urn:oasis:names:tc:opendocument:xmlns:container"}


def chemin_opf(z, container):
    racine = ET.fromstring(z.read(container))
    for f in racine.findall(".//c:rootfile", NS):
        return f.get("full-path")
    raise ValueError("pas de rootfile")


def spine_ordre(z, opf, dossier):
    opf_xml = ET.fromstring(z.read(opf))
    # manifest : id -> href
    manifest = {
        e.get("id"): e.get("href")
        for e in opf_xml.iter() if e.tag.endswith("}item") or e.tag == "item"
    }
    idrefs = [
        e.get("idref")
        for e in opf_xml.iter() if e.tag.endswith("}itemref") or e.tag == "itemref"
    ]
    ordre = []
    for idref in idrefs:
        href = manifest.get(idref)
        if not href:
            continue
        # les href peuvent être URL-encodés
        href = re.sub(r"#.*$", "", href)
        href = href.replace("%20", " ")
        chemin = (dossier / href).as_posix()
        ordre.append(chemin)
    return ordre


class Texte(HTMLParser):
    """Récupère le texte visible ; un saut de paragraphe par </p>."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.morceaux = []
        self.saut = False

    def handle_data(self, data):
        t = data.strip()
        if t:
            if self.morceaux and not self.morceaux[-1].endswith(("\n", " ")):
                self.morceaux.append(" ")
            self.morceaux.append(t)
            self.saut = False

    def handle_endtag(self, tag):
        if tag in ("p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote"):
            self.morceaux.append("\n")
            self.saut = True

    def texte(self):
        return "".join(self.morceaux)


def nettoyer(s):
    # supprime les notes de bas de page epub-type (sup numérotés)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def main():
    epub, sortie = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    z = zipfile.ZipFile(epub)
    opf = chemin_opf(z, next(n for n in z.namelist() if n.endswith("container.xml")))
    dossier = pathlib.Path(opf).parent
    ordre = spine_ordre(z, opf, dossier)
    blocs = []
    for chemin in ordre:
        try:
            brut = z.read(chemin).decode("utf-8", "replace")
        except KeyError:
            continue
        p = Texte()
        p.feed(brut)
        blocs.append(p.texte())
    texte = nettoyer("\n\n".join(blocs))
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(texte, encoding="utf-8")
    mots = len(texte.split())
    print(f"{len(ordre)} fichiers, {mots} mots -> {sortie}")


if __name__ == "__main__":
    main()
