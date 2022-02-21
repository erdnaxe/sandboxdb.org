---
title: API Documentation
---

API uses JSON format.

## Get the list of services

`{{< ref path="service/_index.md" outputFormat="json" >}}`

## Get information about a service

For example, to get `NetworkManager.service` information, you can query:
`{{< ref path="service/NetworkManager.service.md" outputFormat="json" >}}`

When services allow multiple instances, their name ends with `@` symbol.
This symbol is remplaced by `-` in URLs.
For example, to get `apache2@.service` information, you can query:
`{{< ref path="service/apache2-.service.md" outputFormat="json" >}}`
