export function embedTermly() {
  (function (d, s, id) {
    var js;
    if (d.getElementById(id)) return;
    js = d.createElement(s) as HTMLScriptElement;
    js.id = id;
    js.src = 'https://app.termly.io/embed-policy.min.js';
    document.head.appendChild(js);
  })(document, 'script', 'termly-jssdk');
}
