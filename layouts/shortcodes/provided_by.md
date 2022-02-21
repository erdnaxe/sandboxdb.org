{{ $data := index $.Site.Data.service (.Get 0) }}

This unit is provided by:
{{ range $data.provided_by }}
  * {{ partial "upstream_logo.html" . }} [{{ replace . "/" "/<wbr>" | safeHTML }}]({{ . | safeHTML }})
{{ end }}
