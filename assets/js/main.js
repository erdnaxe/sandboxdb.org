import * as params from '@params';
import autoComplete from "js/autoComplete.js";

const autoCompleteJS = new autoComplete({
    data: {
        src: fetch(params.indexUrl).then((d) => d.json()),
        key: ["title"],
        cache: true
    },
    highlight: true,
    resultsList: {
        render: true
    },
    resultItem: {
        content: (data, source) => {
            source.innerHTML = data.match;
        }
    },
    onSelection: feedback => {
        // Go to page
        window.location.href = feedback.selection.value.uri;
    }
});