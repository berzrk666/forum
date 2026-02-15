const routes = [];

export function addRoute(pattern, handler) {
  routes.push({ pattern, handler });
}

export function navigate(hash) {
  window.location.hash = hash;
}

export function resolve() {
  const hash = window.location.hash || "#/";
  const path = hash.slice(1); // remove leading #

  for (const route of routes) {
    const match = matchRoute(route.pattern, path);
    if (match) {
      return route.handler(match.params);
    }
  }

  return null;
}

function matchRoute(pattern, path) {
  const patternParts = pattern.split("/").filter(Boolean);
  const pathParts = path.split("/").filter(Boolean);

  if (patternParts.length !== pathParts.length) return null;

  const params = {};

  for (let i = 0; i < patternParts.length; i++) {
    if (patternParts[i].startsWith(":")) {
      params[patternParts[i].slice(1)] = pathParts[i];
    } else if (patternParts[i] !== pathParts[i]) {
      return null;
    }
  }

  return { params };
}
