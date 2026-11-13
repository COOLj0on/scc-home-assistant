# Chriselec SCC

Copyright (C) 2026 COOLj0on. Licensed under GNU AGPL-3.0-only; see [LICENSE](LICENSE).

Intégration personnalisée Home Assistant pour les régulateurs Chriselec Grandis
650 HK. Elle interroge `medius_val.xml` à intervalle configurable et propose les
31 valeurs décodées par le flow Node-RED SCC comme capteurs Home Assistant.

## Configuration

Ajouter l'intégration depuis **Paramètres → Appareils et services → Ajouter une
intégration → Chriselec SCC**. Saisir l'adresse du contrôleur; le chemin par
défaut est `/medius_val.xml`. Des identifiants HTTP Basic sont facultatifs.
À l'installation, tous les capteurs sont présélectionnés; choisir ceux à créer
et une fréquence de 5 à 3600 secondes (30 secondes par défaut). Ces paramètres,
l'adresse, le chemin et les identifiants restent modifiables dans **Configurer**.
Le formulaire permet aussi d'affecter chaque sonde à son emplacement (haut,
milieu et bas du ballon, départ et retour solaire, poêle bouilleur) et de
sélectionner les pompes de chaque circuit. Les sondes affectées sont créées
automatiquement même si elles n'étaient pas cochées dans la liste générale.

## Carte du ballon tampon

L'intégration fournit une carte Lovelace qui affiche les trois températures du
ballon, les températures départ/retour solaire, celle du poêle et l'état des
pompes sélectionnées. Après le premier démarrage de l'intégration, ajouter la
ressource **Paramètres → Tableaux de bord → Ressources** avec l'URL
`/scc/scc-thermal-card.js` et le type **Module JavaScript**. Ajouter ensuite une
carte manuelle de type `custom:scc-thermal-card` au tableau de bord. Les sondes
et pompes affectées dans la configuration de l'intégration sont détectées
automatiquement par la carte.
Si plusieurs régulateurs SCC sont configurés, renseigner `controller_entity`
dans la configuration YAML de la carte avec l'identifiant d'une entité SCC du
régulateur à afficher.

Les sondes S1–S10 et F1S1–F1S4 sont publiées en °C. Les registres R0–R7 et
HE1–HE3 sont publiés en %. Les unités des registres Str, Q1 et Q2 restent à
préciser. Les sondes au-dessus de la limite valide du protocole passent à l'état
inconnu plutôt qu'à `0`; une réponse mal formée rend les capteurs indisponibles.
Si des identifiants HTTP Basic sont utilisés, préférer HTTPS ou un réseau local
de confiance.

Les entités Node-RED déjà présentes ont leurs propres identifiants de registre.
Cette intégration ne les reprend pas automatiquement : pendant la validation,
les deux sources peuvent donc coexister avec des entités en double. Ne désactive
pas le flow avant d'avoir vérifié les nouvelles entités et leurs identifiants.

## HACS / Marketplace

Le dépôt public est [COOLj0on/scc-home-assistant](https://github.com/COOLj0on/scc-home-assistant).
Dans HACS/Marketplace, ajouter cette URL comme dépôt personnalisé de type
**Intégration**, puis installer la version `v0.1.0`. Pour les versions suivantes,
mettre à jour la version dans `manifest.json` et créer une release GitHub avec
le même numéro.

## Développement

Exécuter les tests du parseur avec :

```powershell
python -m unittest discover -s tests -v
```
