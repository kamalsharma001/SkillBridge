export interface RoleMatchResult {
  roleId: string;
  roleName: string;
  category: string;
  matchPercent: number;
  matchedSkills: string[];
  missingSkills: string[];
  skillScore: number;
  roleScore: number;
  tier: "high" | "moderate" | "low";
  tierLabel: string;
  readinessStatus: string;
}

interface RoleDefinition {
  id: string;
  name: string;
  category: string;
  // Core domain-specific skills (high weight)
  coreKeywords: string[];
  // Adjacent / transferable skills (moderate weight)
  relatedKeywords: string[];
  // Anchor keywords - at least one must be present to exceed 55%
  domainAnchors: string[];
  // Realistic salary & demand metadata
  salary: string;
  yoyGrowth: string;
  marketDemand: string;
}

export const ROLE_TAXONOMY: RoleDefinition[] = [
  {
    id: "ml-engineer",
    name: "Machine Learning Engineer",
    category: "AI & Data Science",
    coreKeywords: [
      "pytorch",
      "tensorflow",
      "keras",
      "hugging face",
      "huggingface",
      "transformers",
      "vector database",
      "vector databases",
      "milvus",
      "chroma",
      "pinecone",
      "rag",
      "deep learning",
      "neural networks",
      "nlp",
      "computer vision",
      "llm",
      "large language models",
      "scikit-learn",
      "cuda",
      "vllm",
      "lora",
      "peft",
      "deepspeed",
      "mlops",
      "model training",
      "fine-tuning",
    ],
    relatedKeywords: [
      "python",
      "fastapi",
      "docker",
      "pandas",
      "numpy",
      "sql",
      "git",
      "linux",
      "math",
      "statistics",
      "data science",
      "machine learning",
    ],
    domainAnchors: ["pytorch", "tensorflow", "deep learning", "nlp", "computer vision", "llm", "rag", "transformers", "scikit-learn", "machine learning"],
    salary: "$168,000 - $215,000 / yr",
    yoyGrowth: "+29.2% YoY",
    marketDemand: "Very High (Top 3 Tech Specializations)",
  },
  {
    id: "fullstack-dev",
    name: "Full Stack Developer",
    category: "Web & Enterprise",
    coreKeywords: [
      "react",
      "next.js",
      "nextjs",
      "typescript",
      "javascript",
      "node.js",
      "nodejs",
      "vue",
      "angular",
      "fastapi",
      "django",
      "flask",
      "express",
      "html",
      "css",
      "tailwind",
      "frontend",
      "backend",
      "full stack",
      "fullstack",
      "rest api",
      "rest apis",
      "graphql",
      "web development",
    ],
    relatedKeywords: [
      "python",
      "postgresql",
      "sql",
      "mongodb",
      "redis",
      "docker",
      "git",
      "api",
      "mysql",
      "linux",
      "json",
      "jwt",
    ],
    domainAnchors: ["react", "next.js", "nextjs", "node.js", "nodejs", "typescript", "javascript", "full stack", "frontend", "django", "fastapi", "express", "web development"],
    salary: "₹28 - ₹42 LPA / $145,000 / yr",
    yoyGrowth: "+18.6% YoY",
    marketDemand: "High & Steady (Core Industry Pillar)",
  },
  {
    id: "devops-sre",
    name: "Cloud DevOps / SRE",
    category: "Infrastructure & Platform",
    coreKeywords: [
      "kubernetes",
      "k8s",
      "terraform",
      "helm",
      "aws",
      "azure",
      "gcp",
      "ci/cd",
      "github actions",
      "gitlab ci",
      "jenkins",
      "prometheus",
      "grafana",
      "sre",
      "devops",
      "ansible",
      "argocd",
      "argo",
      "cloudformation",
      "infrastructure as code",
      "iac",
      "site reliability",
      "docker swarm",
    ],
    relatedKeywords: [
      "docker",
      "linux",
      "bash",
      "shell",
      "python",
      "networking",
      "git",
      "cloud",
      "security",
      "monitoring",
    ],
    domainAnchors: ["kubernetes", "k8s", "terraform", "aws", "azure", "gcp", "ci/cd", "devops", "sre", "jenkins", "argocd", "ansible"],
    salary: "$172,000 - $210,000 / yr",
    yoyGrowth: "+24.8% YoY",
    marketDemand: "Critical Demand (Industry Talent Shortage)",
  },
  {
    id: "data-scientist",
    name: "Data Scientist",
    category: "AI & Data Science",
    coreKeywords: [
      "statistics",
      "statistical",
      "pandas",
      "numpy",
      "scikit-learn",
      "r",
      "tableau",
      "power bi",
      "a/b testing",
      "hypothesis testing",
      "regression",
      "dbt",
      "snowflake",
      "data analysis",
      "data analytics",
      "data science",
      "data scientist",
      "eda",
      "econometrics",
      "causal inference",
      "bigquery",
      "spark",
      "pyspark",
      "databricks",
    ],
    relatedKeywords: [
      "python",
      "sql",
      "data modeling",
      "jupyter",
      "matplotlib",
      "seaborn",
      "excel",
      "git",
      "machine learning",
    ],
    domainAnchors: ["statistics", "statistical", "pandas", "data science", "data analysis", "tableau", "a/b testing", "scikit-learn", "dbt", "snowflake", "r"],
    salary: "$148,000 - $185,000 / yr",
    yoyGrowth: "+21.3% YoY",
    marketDemand: "High (Product Analytics & Decision Science)",
  },
  {
    id: "cybersecurity",
    name: "Cybersecurity Analyst",
    category: "Security & Governance",
    coreKeywords: [
      "siem",
      "splunk",
      "sentinel",
      "wireshark",
      "nessus",
      "soc",
      "owasp",
      "incident response",
      "threat intelligence",
      "penetration testing",
      "pentesting",
      "vulnerability assessment",
      "cissp",
      "security+",
      "ceh",
      "ethical hacking",
      "malware",
      "firewall",
      "ids",
      "ips",
      "mitre",
      "cybersecurity",
      "infosec",
      "appsec",
      "cryptography",
      "zero trust",
      "burp suite",
    ],
    relatedKeywords: [
      "network security",
      "linux",
      "bash",
      "python",
      "iam",
      "audit",
      "compliance",
      "soc2",
      "security",
    ],
    domainAnchors: ["siem", "splunk", "wireshark", "soc", "owasp", "incident response", "penetration testing", "cissp", "security+", "ceh", "cybersecurity", "infosec", "threat intelligence"],
    salary: "$152,000 - $190,000 / yr",
    yoyGrowth: "+31.5% YoY",
    marketDemand: "Extremely High (Zero Unemployment Field)",
  },
  {
    id: "backend-architect",
    name: "Backend Systems Architect",
    category: "Infrastructure & Platform",
    coreKeywords: [
      "go",
      "golang",
      "grpc",
      "protocol buffers",
      "protobuf",
      "raft",
      "distributed systems",
      "concurrency",
      "multithreading",
      "goroutines",
      "kafka",
      "rocksdb",
      "low latency",
      "system design",
      "consensus",
      "c++",
      "rust",
      "database internals",
      "high throughput",
      "microservices architecture",
    ],
    relatedKeywords: [
      "postgresql",
      "sql",
      "redis",
      "docker",
      "linux",
      "python",
      "microservices",
      "caching",
      "architecture",
      "git",
    ],
    domainAnchors: ["go", "golang", "grpc", "distributed systems", "concurrency", "raft", "kafka", "system design", "low latency", "microservices"],
    salary: "$178,000 - $225,000 / yr",
    yoyGrowth: "+22.4% YoY",
    marketDemand: "Very High in Fintech, Cloud & Distributed Systems",
  },
  {
    id: "tech-pm",
    name: "Technical Product Manager",
    category: "Product & Strategy",
    coreKeywords: [
      "product management",
      "prd",
      "prds",
      "product roadmap",
      "roadmap",
      "agile",
      "scrum",
      "product owner",
      "user stories",
      "wireframes",
      "jira",
      "user journey",
      "gtm",
      "go to market",
      "stakeholder management",
      "product strategy",
      "customer discovery",
      "mixpanel",
      "amplitude",
      "competitive analysis",
      "technical product manager",
    ],
    relatedKeywords: [
      "sql",
      "analytics",
      "a/b testing",
      "kpis",
      "metrics",
      "leadership",
      "communication",
      "software development",
    ],
    domainAnchors: ["product management", "prd", "roadmap", "agile", "scrum", "product owner", "user stories", "jira", "gtm", "product strategy"],
    salary: "$175,000 - $220,000 / yr",
    yoyGrowth: "+20.1% YoY",
    marketDemand: "Very High for Developer-Facing Platforms",
  },
  {
    id: "mobile-dev",
    name: "Mobile Applications Developer",
    category: "Mobile & Client",
    coreKeywords: [
      "flutter",
      "dart",
      "react native",
      "ios",
      "swift",
      "swiftui",
      "objective-c",
      "android",
      "kotlin",
      "mobile app",
      "mobile development",
      "fastlane",
      "xcode",
      "android studio",
      "app store",
      "play store",
      "sqlite",
      "realm",
      "bloc",
      "expo",
    ],
    relatedKeywords: [
      "typescript",
      "javascript",
      "react",
      "ui",
      "ux",
      "mobile",
      "rest api",
      "graphql",
      "git",
    ],
    domainAnchors: ["flutter", "dart", "react native", "swift", "kotlin", "ios", "android", "mobile app", "mobile development", "xcode", "android studio"],
    salary: "$138,000 - $175,000 / yr",
    yoyGrowth: "+16.2% YoY",
    marketDemand: "Steady Demand for Cross-Platform Specialists",
  },
];

function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function testKeywordMatch(keyword: string, skillNames: string[], fullText: string): boolean {
  const k = keyword.toLowerCase().trim();
  if (!k) return false;

  // 1. Exact match or whole-token match in candidate's skills array
  for (const skill of skillNames) {
    if (skill === k) return true;
    if (k.length > 2 && (skill.startsWith(`${k} `) || skill.endsWith(` ${k}`) || skill.includes(` ${k} `))) {
      return true;
    }
    // Handle simple plurals (e.g. "vector database" vs "vector databases")
    if (k + "s" === skill || skill + "s" === k) return true;
  }

  // 2. Standalone word boundary match in full resume / project text
  const escaped = escapeRegex(k);
  // Match word boundaries: e.g. "python", "python3", "react", "react.js"
  const regex = new RegExp(`(?:^|[^a-z0-9])${escaped}(?:s|js|3)?(?:$|[^a-z0-9])`, "i");
  return regex.test(fullText);
}

/**
 * Computes semantic keyword overlap and realistic match percentage
 * between candidate profile signals and the 8 target roles.
 */
export function evaluateCandidateRoleMatches(
  skills: { name: string }[] = [],
  currentRole: string = "",
  projects: { name?: string; description?: string }[] = [],
  experienceYears: number = 0
): Record<string, RoleMatchResult> {
  // Normalize candidate skill list
  const skillNames = skills
    .map((s) => (s.name || "").toLowerCase().trim())
    .filter(Boolean);

  // Build full lowercase text corpus for boundary search
  const projectCorpus = projects
    .map((p) => `${p.name || ""} ${p.description || ""}`)
    .join(" ");
  const fullCorpus = ` ${skillNames.join(" ")} ${currentRole} ${projectCorpus} `.toLowerCase();

  const roleRaw = currentRole.toLowerCase().trim();
  const results: Record<string, RoleMatchResult> = {};

  ROLE_TAXONOMY.forEach((roleDef) => {
    // 1. Check core domain keyword matches
    const matchedCore = roleDef.coreKeywords.filter((k) =>
      testKeywordMatch(k, skillNames, fullCorpus)
    );

    // 2. Check related / transferable keyword matches
    const matchedRelated = roleDef.relatedKeywords.filter((k) =>
      testKeywordMatch(k, skillNames, fullCorpus)
    );

    // 3. Check domain anchor presence
    const hasDomainAnchor = roleDef.domainAnchors.some((anchor) =>
      testKeywordMatch(anchor, skillNames, fullCorpus)
    );

    // 4. Role title semantic similarity
    const roleWords = roleDef.name.toLowerCase().split(/[\s/]+/);
    const roleTitleMatch = roleWords.filter((w) => roleRaw.includes(w) && w.length > 2);
    const roleScore = Math.min(95, Math.round(roleTitleMatch.length * 35 + (roleRaw ? 20 : 0)));

    // 5. Calculate weighted score:
    // Base foundation: 18% (basic engineering background)
    let rawScore = 18;

    // Core domain matches (up to 55 points)
    const corePoints = Math.min(55, matchedCore.length * 14);
    rawScore += corePoints;

    // Related / transferable matches (up to 18 points)
    const relatedPoints = Math.min(18, matchedRelated.length * 4);
    rawScore += relatedPoints;

    // Title / role alignment boost (up to 12 points)
    if (roleTitleMatch.length > 0) {
      rawScore += Math.min(12, roleTitleMatch.length * 6);
    }

    // Experience boost
    if (experienceYears > 0) {
      rawScore += Math.min(6, Math.round(experienceYears * 1.5));
    }

    // CRITICAL DOMAIN GUARDRAIL:
    // If the candidate has ZERO domain anchor keywords (e.g. applying for Cybersecurity
    // without any security/SIEM/OWASP/SOC skills, or Mobile without Flutter/Swift/Android),
    // strictly cap the match in the 18% - 32% range so it never unrealistically claims 70-80%!
    if (!hasDomainAnchor) {
      rawScore = Math.min(32, Math.max(18, Math.round(rawScore * 0.45)));
    } else {
      // If domain anchor is present, ensure score is at least 52% and clamp realistically
      rawScore = Math.max(52, Math.min(94, rawScore));
    }

    const finalMatchPercent = Math.round(rawScore);

    // Classify tier
    let tier: "high" | "moderate" | "low" = "low";
    let tierLabel = "Low Alignment";
    let readinessStatus = "Significant Skill Divergence (Career Pivot Required)";

    if (finalMatchPercent >= 75) {
      tier = "high";
      tierLabel = "Strong Alignment";
      readinessStatus = "Tier-1 Enterprise Alignment (Interview Ready)";
    } else if (finalMatchPercent >= 50) {
      tier = "moderate";
      tierLabel = "Moderate Fit";
      readinessStatus = "Moderate Alignment (Targeted Competency Gaps)";
    }

    // Determine missing skills from the role's primary curriculum
    const missing = roleDef.coreKeywords
      .filter((k) => !matchedCore.includes(k))
      .slice(0, 5);

    results[roleDef.id] = {
      roleId: roleDef.id,
      roleName: roleDef.name,
      category: roleDef.category,
      matchPercent: finalMatchPercent,
      matchedSkills: matchedCore.concat(matchedRelated).slice(0, 8),
      missingSkills: missing,
      skillScore: Math.min(95, Math.round(finalMatchPercent * 1.05)),
      roleScore: Math.max(20, Math.min(90, roleScore)),
      tier,
      tierLabel,
      readinessStatus,
    };
  });

  return results;
}
