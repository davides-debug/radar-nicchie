# Ricerca Etsy Open API v3

Per integrare Etsy nel sistema Radar-Nicchie, è necessaria l'API ufficiale. Ecco i dettagli della ricerca:

## Accessibilità e Requisiti
- **API Version**: Open API v3 (REST).
- **Registrazione**: Richiesta tramite il portale [Etsy Developers](https://www.etsy.com/developers).
- **Autenticazione**: OAuth 2.0.
- **Approvazione**: Una volta creata l'app, Etsy deve approvarla prima che la chiave API diventi attiva (solitamente 24-48 ore).
- **Sicurezza**: Richiede l'attivazione dell'autenticazione a due fattori (2FA) sull'account Etsy.

## Casi d'Uso per Radar-Nicchie
L'API permette di cercare listing (`findAllListingsActive`) filtrando per keyword. Questo può essere usato per tracciare:
- Numero di prodotti attivi per una nicchia.
- Prezzo medio dei listing.
- Tag popolari associati.

## Conclusione
L'integrazione è possibile ma richiede un intervento manuale iniziale dell'utente per registrare l'app e ottenere le credenziali. Una volta ottenute, il modulo potrà essere implementato in modo simile a Udemy.
