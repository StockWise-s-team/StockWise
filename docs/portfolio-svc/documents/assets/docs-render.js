(function (window, document) {
  "use strict";

  var config = window.StockWiseDocs;
  var app = document.getElementById("docs-app");
  var pageId = document.documentElement.getAttribute("data-doc-page") || "index";
  var isIndexPage = pageId === "index";

  if (!config || !app) {
    return;
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function getGroup(id) {
    return config.groups.find(function (group) {
      return group.id === id;
    });
  }

  function pathFromCurrent(path) {
    if (!path) {
      return "";
    }

    if (/^(?:[a-z]+:)?\/\//i.test(path) || path.indexOf("#") === 0) {
      return path;
    }

    if (isIndexPage) {
      return path;
    }

    return path.indexOf("groups/") === 0 ? path.slice("groups/".length) : "../" + path;
  }

  function topbar() {
    var traceabilityGroup = getGroup("traceability");
    var traceabilityHref = traceabilityGroup ? traceabilityGroup.file : "groups/traceability.html";
    var authoringGuideLink = config.authoringGuide
      ? '      <a href="' + escapeHtml(pathFromCurrent(config.authoringGuide)) + '">Authoring guide</a>'
      : "";

    return [
      '<header class="topbar">',
      '  <div class="topbar-inner">',
      '    <a class="brand" href="' + escapeHtml(pathFromCurrent("index.html")) + '">' + escapeHtml(config.serviceName) + " docs</a>",
      '    <nav class="topnav" aria-label="Primary navigation">',
      '      <a href="' + escapeHtml(pathFromCurrent("index.html")) + '">Index</a>',
      '      <a href="' + escapeHtml(pathFromCurrent(traceabilityHref)) + '">Traceability</a>',
      authoringGuideLink,
      "    </nav>",
      "  </div>",
      "</header>"
    ].join("");
  }

  function sideNav(activeId) {
    var links = config.groups.map(function (group) {
      var active = group.id === activeId ? ' class="active"' : "";
      return '<a' + active + ' href="' + escapeHtml(pathFromCurrent(group.file)) + '">' + escapeHtml(group.title) + "</a>";
    }).join("");

    return [
      '<aside class="side-nav" aria-label="Document groups">',
      "  <strong>Groups</strong>",
      '  <a href="' + escapeHtml(pathFromCurrent("index.html")) + '">Documentation Hub</a>',
      links,
      "</aside>"
    ].join("");
  }

  function metricRow(items) {
    return '<div class="metric-row" aria-label="Documentation inventory">' +
      items.map(function (item) {
        return '<span class="metric">' + escapeHtml(item) + "</span>";
      }).join("") +
      "</div>";
  }

  function groupCard(group) {
    return [
      '<a class="group-card" href="' + escapeHtml(pathFromCurrent(group.file)) + '">',
      "  <div>",
      '    <p class="eyebrow">' + escapeHtml(group.eyebrow) + "</p>",
      "    <h2>" + escapeHtml(group.title) + "</h2>",
      "    <p>" + escapeHtml(group.description) + "</p>",
      "  </div>",
      '  <div class="group-meta">',
      "    <span>" + escapeHtml(group.range) + "</span>",
      '    <span class="open-label">Open group</span>',
      "  </div>",
      "</a>"
    ].join("");
  }

  function artifactCard(artifact) {
    var artifactHref = pathFromCurrent(artifact.href);

    return [
      '<article class="artifact">',
      '  <div class="artifact-header">',
      "    <div>",
      '      <p class="eyebrow">' + escapeHtml(artifact.eyebrow) + "</p>",
      "      <h2>" + escapeHtml(artifact.title) + "</h2>",
      "      <p>" + escapeHtml(artifact.description) + "</p>",
      "    </div>",
      '    <a class="button" href="' + escapeHtml(artifactHref) + '">Open file</a>',
      "  </div>",
      '  <iframe class="preview-frame" loading="lazy" title="' + escapeHtml(artifact.frameTitle) + '" src="' + escapeHtml(artifactHref) + '"></iframe>',
      "</article>"
    ].join("");
  }

  function directArtifactHref(artifact) {
    return artifact.anchor ? artifact.href + "#" + artifact.anchor : artifact.href;
  }

  function childArtifactGroup(group) {
    var rows = group.artifacts.map(function (artifact) {
      return [
        "<tr>",
        '  <td><span class="artifact-id">' + escapeHtml(artifact.eyebrow) + "</span></td>",
        '  <td><a href="' + escapeHtml(pathFromCurrent(directArtifactHref(artifact))) + '">' + escapeHtml(artifact.title) + "</a></td>",
        "  <td>" + escapeHtml(artifact.description) + "</td>",
        '  <td><a href="' + escapeHtml(pathFromCurrent(group.file)) + '">' + escapeHtml(group.title) + "</a></td>",
        "</tr>"
      ].join("");
    }).join("");

    return [
      '<section class="panel artifact-index-group">',
      "  <h3>" + escapeHtml(group.title) + "</h3>",
      '  <div class="table-wrap">',
      "    <table>",
      "      <thead><tr><th>ID</th><th>Artifact</th><th>Description</th><th>Group</th></tr></thead>",
      "      <tbody>",
      rows,
      "      </tbody>",
      "    </table>",
      "  </div>",
      "</section>"
    ].join("");
  }

  function renderIndex() {
    document.title = "Portfolio Service Documentation";
    app.innerHTML = [
      topbar(),
      '<section class="hero">',
      '  <div class="hero-inner">',
      '    <p class="eyebrow">' + escapeHtml(config.serviceName) + "</p>",
      "    <h1>Documentation Hub</h1>",
      "    <p>" + escapeHtml(config.projectSummary || "Grouped entry point for the service documentation set.") + "</p>",
      metricRow(config.metrics),
      "  </div>",
      "</section>",
      '<main class="content">',
      '  <section class="group-grid" aria-label="Documentation groups">',
      config.groups.map(groupCard).join(""),
      "  </section>",
      '  <section class="artifact-index" aria-label="Direct child artifact links">',
      "    <header class=\"page-heading\">",
      "      <p class=\"eyebrow\">Direct artifact links</p>",
      "      <h2>Child Documents</h2>",
      "      <p>Every child HTML artifact is directly reachable from this index, as required by the documentation skill contract.</p>",
      "    </header>",
      config.groups.map(childArtifactGroup).join(""),
      "  </section>",
      '  <section class="workflow-band" aria-label="Documentation workflow">',
      '    <div class="panel">',
      "      <h2>How To Read This Set</h2>",
      "      <p>Start with Overview and Use Cases for behavior, then follow linked IDs into Functional Requirements, Business Rules, Data Models, API Contracts, Business Flows, and State Diagrams. Use Traceability to verify coverage.</p>",
      "    </div>",
      '    <div class="panel">',
      "      <h2>Authoring Contract</h2>",
      "      <p>This documentation set is generated from the current project source, shared inventory data, and modular child artifacts.</p>",
      "    </div>",
      "  </section>",
      "</main>"
    ].join("");
  }

  function renderGroup(group) {
    document.title = group.title + " - " + config.serviceName;
    app.innerHTML = [
      topbar(),
      '<main class="doc-layout">',
      sideNav(group.id),
      '  <section class="doc-stack">',
      '    <header class="page-heading">',
      '      <p class="eyebrow">' + escapeHtml(group.eyebrow) + "</p>",
      "      <h1>" + escapeHtml(group.title) + "</h1>",
      "      <p>" + escapeHtml(group.description) + "</p>",
      "    </header>",
      group.artifacts.map(artifactCard).join(""),
      "  </section>",
      "</main>"
    ].join("");
  }

  if (pageId === "index") {
    renderIndex();
    return;
  }

  var group = getGroup(pageId);
  if (group) {
    renderGroup(group);
  } else {
    app.innerHTML = topbar() + '<main class="content"><section class="panel"><h1>Document group not found</h1><p>The requested documentation group is not registered in <code>assets/docs-data.js</code>.</p></section></main>';
  }
})(window, document);
