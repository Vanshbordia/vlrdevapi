import { assetUrl, canonicalUrl } from './shared';

/**
 * Project facts mirrored from the Python package metadata in `pyproject.toml`
 * ([project] name/version/urls, classifiers). Keep in sync with a version bump.
 */
export const project = {
  name: 'VLRdevAPI',
  version: '2.4.1',
  description:
    'A type-safe Python SDK for Valorant esports data from VLR.gg. Fetch match results, player stats, team rosters, and tournament brackets through a fully typed Python interface.',
  licenseUrl: 'https://opensource.org/license/mit',
  programmingLanguage: 'Python',
  runtimePlatform: 'Python 3.11+',
  repositoryUrl: 'https://github.com/vanshbordia/vlrdevapi',
  packageUrl: 'https://pypi.org/project/vlrdevapi/',
  githubProfileUrl: 'https://github.com/vanshbordia',
  author: 'Vansh Bordia',
} as const;

/** Canonical URLs reused across structured data. */
export const projectUrls = {
  home: canonicalUrl('/'),
  docs: canonicalUrl('/docs/'),
  logo: assetUrl('/logo.png'),
} as const;

/** Profiles that identify the same project across the web. */
export const projectSameAs = [project.repositoryUrl, project.packageUrl] as const;

/**
 * Author and publisher nodes reused by JSON-LD. VLRdevAPI is its own entity;
 * the author is linked to the maintainer's GitHub profile.
 */
export const projectAuthor = {
  '@type': 'Person',
  name: project.author,
  url: project.githubProfileUrl,
} as const;

export const projectPublisher = {
  '@type': 'Organization',
  name: project.name,
  url: projectUrls.home,
  logo: {
    '@type': 'ImageObject',
    url: projectUrls.logo,
  },
  sameAs: projectSameAs,
} as const;

/**
 * Package keywords, mirrored from the `keywords` field in `pyproject.toml`
 * and used for page metadata.
 */
export const projectKeywords = [
  'Valorant esports API',
  'VLR.gg API',
  'vlrgg API',
  'Python SDK',
  'Valorant match data',
  'Valorant player statistics',
  'Python Valorant API',
  'Valorant API without key',
  'free Valorant API',
  'esports data API',
  'VCT data',
  'esports web scraping alternative',
];
