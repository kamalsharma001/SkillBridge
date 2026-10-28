export interface DemoProfileData {
  id: string;
  roleName: string;
  category: string;
  matchPercent: number;
  candidate: {
    name: string;
    email: string;
    current_role: string;
    location: string;
    experience_years: number;
    education: string[];
    skills: { name: string }[];
    projects: { name: string; description?: string }[];
    certifications: string[];
  };
  readiness: {
    readiness_score: number;
    status: string;
    breakdown: {
      skill_match: number;
      role_alignment: number;
      experience_match: number;
      education_match: number;
    };
  };
  matched_opportunities: {
    title: string;
    company: string;
    compatibility_score: number;
    salary: string;
    location: string;
    breakdown: {
      skill_match: number;
      role_alignment: number;
      experience_match: number;
    };
    why_matched: string[];
    gaps: string[];
  }[];
  learning_plan: {
    course_title: string;
    skill: string;
    platform: string;
    priority: "high" | "medium";
    duration_hours: number;
    match_confidence: number;
    relevance_reason: string;
  }[];
  skill_gaps: {
    skill: string;
    current_level: number;
    required_level: number;
    priority: "high" | "medium";
    category: string;
  }[];
  industry_intelligence: {
    market_demand: string;
    yoy_growth: string;
    avg_salary: string;
    top_skills_trending: string[];
    key_takeaway: string;
  };
  agent_summaries: {
    career_readiness: string;
    skill_analysis: string;
    learning: string;
    opportunity: string;
    industry_intelligence: string;
    profile_intelligence: string;
  };
}

export const DEMO_PROFILES: DemoProfileData[] = [
  // 1. Machine Learning Engineer
  {
    id: "ml-engineer",
    roleName: "Machine Learning Engineer",
    category: "AI & Data Science",
    matchPercent: 88,
    candidate: {
      name: "Alex Chen",
      email: "alex.chen@skillbridge.ai",
      current_role: "Associate AI Engineer",
      location: "San Francisco, CA (Open to Remote)",
      experience_years: 2.5,
      education: [
        "B.S. in Computer Science & Applied Mathematics, UC Berkeley (GPA: 3.86/4.0)",
        "Deep Learning Specialization, DeepLearning.AI",
      ],
      skills: [
        { name: "Python" },
        { name: "PyTorch" },
        { name: "TensorFlow" },
        { name: "Hugging Face" },
        { name: "Docker" },
        { name: "Scikit-Learn" },
        { name: "SQL" },
        { name: "FastAPI" },
        { name: "Vector Databases" },
        { name: "Git" },
      ],
      projects: [
        {
          name: "Enterprise RAG Pipeline with Hybrid Search",
          description: "Engineered low-latency document QA engine indexing 500k financial filings using Milvus and LangChain with 94ms P99 latency.",
        },
        {
          name: "Vision-Language Fine-Tuning Benchmarks",
          description: "Fine-tuned LLaVA-1.5 models on domain-specific medical imagery with LoRA, achieving 18% higher zero-shot accuracy.",
        },
      ],
      certifications: [
        "AWS Certified Machine Learning - Specialty",
        "DeepLearning.AI Generative AI for Everyone",
      ],
    },
    readiness: {
      readiness_score: 88,
      status: "Tier-1 Enterprise Alignment (Interview Ready)",
      breakdown: {
        skill_match: 91,
        role_alignment: 89,
        experience_match: 84,
        education_match: 92,
      },
    },
    matched_opportunities: [
      {
        title: "Senior Machine Learning Engineer",
        company: "Google Cloud AI",
        compatibility_score: 93,
        salary: "$165,000 - $210,000 / yr",
        location: "Mountain View, CA / Hybrid",
        breakdown: { skill_match: 94, role_alignment: 92, experience_match: 88 },
        why_matched: ["Extensive PyTorch and Transformer architecture mastery", "Demonstrated RAG indexing and vector optimization in production"],
        gaps: ["Distributed GPU cluster management (Slurm/vLLM)", "TensorRT quantization pipelines"],
      },
      {
        title: "AI Inference & Platform Engineer",
        company: "Stripe",
        compatibility_score: 87,
        salary: "$155,000 - $195,000 / yr",
        location: "San Francisco, CA / Remote",
        breakdown: { skill_match: 89, role_alignment: 86, experience_match: 82 },
        why_matched: ["Production FastAPI model serving capabilities", "Solid distributed vector search background"],
        gaps: ["High-throughput Triton Inference Server setup", "Real-time fraud streaming feature stores"],
      },
      {
        title: "Applied Deep Learning Scientist",
        company: "NVIDIA",
        compatibility_score: 84,
        salary: "$170,000 - $225,000 / yr",
        location: "Santa Clara, CA / Remote",
        breakdown: { skill_match: 86, role_alignment: 84, experience_match: 80 },
        why_matched: ["Strong applied mathematics and model calibration grounding", "LoRA/PEFT domain fine-tuning experience"],
        gaps: ["CUDA C++ kernel writing", "Distributed Megatron-LM training"],
      },
    ],
    learning_plan: [
      {
        course_title: "Distributed GPU Training with DeepSpeed & PyTorch FSDP",
        skill: "Distributed Model Training",
        platform: "DeepLearning.AI",
        priority: "high",
        duration_hours: 24,
        match_confidence: 96,
        relevance_reason: "Directly bridges the gap in multi-node training, pipeline parallelism, and zero-redundancy optimizers.",
      },
      {
        course_title: "High-Throughput Model Serving with vLLM & TensorRT-LLM",
        skill: "Inference Optimization",
        platform: "NVIDIA DLI",
        priority: "high",
        duration_hours: 18,
        match_confidence: 93,
        relevance_reason: "Teaches memory-efficient PagedAttention and continuous batching required by enterprise AI platforms.",
      },
      {
        course_title: "Production MLOps: CI/CD for Deep Learning Pipelines",
        skill: "Production MLOps",
        platform: "Coursera (Duke University)",
        priority: "medium",
        duration_hours: 20,
        match_confidence: 89,
        relevance_reason: "Standardizes model versioning, automated drift detection, and canary rollouts on Kubernetes.",
      },
    ],
    skill_gaps: [
      { skill: "Distributed Multi-GPU Training (FSDP / Megatron)", current_level: 42, required_level: 85, priority: "high", category: "AI Systems" },
      { skill: "TensorRT & ONNX Runtime Quantization", current_level: 48, required_level: 80, priority: "high", category: "Inference" },
      { skill: "Kubeflow & Production MLOps Orchestration", current_level: 55, required_level: 85, priority: "medium", category: "DevOps" },
      { skill: "CUDA C++ Profiling & Nsight Systems", current_level: 30, required_level: 70, priority: "medium", category: "Low-level Systems" },
    ],
    industry_intelligence: {
      market_demand: "Very High (Top 3 Tech Growth Specializations)",
      yoy_growth: "+29.2% YoY",
      avg_salary: "$172,000 / yr (Median Enterprise Baseline)",
      top_skills_trending: ["PyTorch", "vLLM", "RAG & Vector Embeddings", "FSDP", "Triton"],
      key_takeaway: "Enterprise migration to self-hosted Small Language Models (SLMs) has accelerated demand for engineers capable of cost-effective local fine-tuning and sub-100ms inference pipelines.",
    },
    agent_summaries: {
      career_readiness: "Candidate presents exceptional algorithmic capabilities and hands-on vector retrieval deployment experience. Score calibrated at 88% readiness based on strong code artifacts and quantitative academic foundation.",
      skill_analysis: "Profile verified across 10 key proficiencies. Deep understanding of Python and PyTorch; priority growth vector centered on distributed multi-node parallelization and inference engine quantization.",
      learning: "Synthesized a targeted 6-week curriculum focusing on high-throughput serving architectures and zero-redundancy optimizers to secure competitive offers in Tier-1 cloud organizations.",
      opportunity: "Correlated profile against 140+ active enterprise openings; identified 3 high-affinity roles exceeding 84% fit at Google Cloud, Stripe, and NVIDIA.",
      industry_intelligence: "AI Engineering demand remains resilient with a 29.2% YoY hiring surge. Technical screening rounds currently prioritize real-world deployment challenges over purely theoretical derivations.",
      profile_intelligence: "Resume shows well-structured impact metrics and clear project ownership. Recommends highlighting throughput gains (e.g. queries per second) alongside accuracy numbers.",
    },
  },

  // 2. Full Stack Developer (Next.js & Python)
  {
    id: "fullstack-dev",
    roleName: "Full Stack Developer",
    category: "Web & Enterprise Applications",
    matchPercent: 82,
    candidate: {
      name: "Priya Sharma",
      email: "priya.sharma@skillbridge.ai",
      current_role: "Software Engineer",
      location: "Bengaluru, India (Open to Hybrid/Remote)",
      experience_years: 3.0,
      education: [
        "B.Tech in Information Technology, NIT Karnataka (GPA: 8.7/10)",
      ],
      skills: [
        { name: "TypeScript" },
        { name: "React" },
        { name: "Next.js" },
        { name: "Node.js" },
        { name: "Python" },
        { name: "FastAPI" },
        { name: "PostgreSQL" },
        { name: "Tailwind CSS" },
        { name: "Docker" },
        { name: "Redis" },
      ],
      projects: [
        {
          name: "Collaborative SaaS Project Workspace",
          description: "Built full-stack Next.js 14 and FastAPI workspace with real-time WebSocket state synchronization and optimistic UI updates.",
        },
        {
          name: "FinTech Transaction Ledger & Analytics",
          description: "Designed ACID-compliant financial ledger system processing 10,000 req/sec backed by PostgreSQL partitioned tables and Redis cache.",
        },
      ],
      certifications: [
        "Meta Certified Front-End Developer",
        "AWS Certified Solutions Architect - Associate",
      ],
    },
    readiness: {
      readiness_score: 82,
      status: "Strong Candidate (Full Stack Alignment)",
      breakdown: {
        skill_match: 86,
        role_alignment: 84,
        experience_match: 80,
        education_match: 88,
      },
    },
    matched_opportunities: [
      {
        title: "Senior Full Stack Engineer",
        company: "Atlassian",
        compatibility_score: 89,
        salary: "₹32 - ₹45 LPA",
        location: "Bengaluru, India / Remote",
        breakdown: { skill_match: 90, role_alignment: 88, experience_match: 85 },
        why_matched: ["High proficiency with TypeScript and Next.js modern state architecture", "Strong SQL transaction handling and Redis caching mastery"],
        gaps: ["Micro-frontend orchestration at scale", "GraphQL federated gateway design"],
      },
      {
        title: "Full Stack Platform Developer",
        company: "Razorpay",
        compatibility_score: 85,
        salary: "₹28 - ₹38 LPA",
        location: "Bengaluru, India / Hybrid",
        breakdown: { skill_match: 88, role_alignment: 85, experience_match: 82 },
        why_matched: ["Solid ACID database design and idempotent API architecture", "Clean responsive modern frontend implementation"],
        gaps: ["High-throughput Kafka event streaming", "Kubernetes service mesh tracing"],
      },
      {
        title: "Software Engineer (Full Stack)",
        company: "Microsoft",
        compatibility_score: 80,
        salary: "₹30 - ₹42 LPA",
        location: "Hyderabad, India / Hybrid",
        breakdown: { skill_match: 84, role_alignment: 80, experience_match: 78 },
        why_matched: ["Robust software craftsmanship and clean architectural layering", "FastAPI backend performance profiling"],
        gaps: ["Azure Cloud enterprise identity (Entra ID)", "Distributed tracing with OpenTelemetry"],
      },
    ],
    learning_plan: [
      {
        course_title: "Advanced Next.js App Router Architecture & Server Actions",
        skill: "Modern React Systems",
        platform: "Frontend Masters",
        priority: "high",
        duration_hours: 16,
        match_confidence: 94,
        relevance_reason: "Master streaming SSR, selective hydration, and edge-rendered micro-frontends.",
      },
      {
        course_title: "Event-Driven Microservices with Apache Kafka & Python",
        skill: "Distributed Messaging",
        platform: "Coursera",
        priority: "high",
        duration_hours: 22,
        match_confidence: 91,
        relevance_reason: "Expands synchronous REST API skills into high-throughput asynchronous pub/sub architectures.",
      },
    ],
    skill_gaps: [
      { skill: "Apache Kafka & Event-Driven Architecture", current_level: 40, required_level: 80, priority: "high", category: "Backend Architecture" },
      { skill: "GraphQL Federation & Apollo Gateway", current_level: 45, required_level: 75, priority: "medium", category: "API Design" },
      { skill: "OpenTelemetry Distributed Tracing", current_level: 35, required_level: 70, priority: "medium", category: "Observability" },
    ],
    industry_intelligence: {
      market_demand: "High & Steady (Core Industry Pillar)",
      yoy_growth: "+18.6% YoY",
      avg_salary: "₹30.5 LPA (Senior Full Stack Baseline)",
      top_skills_trending: ["TypeScript", "Next.js", "FastAPI", "Kafka", "PostgreSQL", "Redis"],
      key_takeaway: "Modern enterprise full-stack hiring has shifted toward developers who excel at edge rendering, state synchronization, and high-concurrency database queries.",
    },
    agent_summaries: {
      career_readiness: "Demonstrates balanced capabilities across UI rendering and backend server performance. Scored at 82% readiness with immediate qualification for product engineering positions.",
      skill_analysis: "Frontend proficiency with Next.js and TypeScript is upper quartile. Backend API development is solid; recommendation is to deepen familiarity with distributed asynchronous queues.",
      learning: "Curated modules emphasize event-driven streaming with Apache Kafka and production OpenTelemetry instrumentation to solidify senior engineering profile.",
      opportunity: "Top compatibility matches found at Atlassian, Razorpay, and Microsoft with strong cultural and technical alignment.",
      industry_intelligence: "Full-stack roles with TypeScript and Python capabilities command an 18.6% hiring premium over single-stack profiles in APAC tech hubs.",
      profile_intelligence: "Clear repository links and architectural project summaries. Strong technical portfolio presentation.",
    },
  },

  // 3. Cloud DevOps & SRE Specialist
  {
    id: "devops-sre",
    roleName: "Cloud DevOps / SRE",
    category: "Infrastructure & Platform Engineering",
    matchPercent: 91,
    candidate: {
      name: "Marcus Vance",
      email: "marcus.vance@skillbridge.ai",
      current_role: "DevOps Engineer",
      location: "Austin, TX (Remote Available)",
      experience_years: 4.0,
      education: [
        "B.S. in Computer Engineering, Texas A&M University",
      ],
      skills: [
        { name: "Kubernetes (K8s)" },
        { name: "Terraform" },
        { name: "AWS Cloud" },
        { name: "Docker" },
        { name: "CI/CD (GitHub Actions / GitLab)" },
        { name: "Linux Administration" },
        { name: "Prometheus & Grafana" },
        { name: "Python / Bash Scripting" },
        { name: "Helm" },
        { name: "Security Hardening" },
      ],
      projects: [
        {
          name: "Multi-Region Kubernetes Disaster Recovery Framework",
          description: "Architected multi-cluster GitOps deployment with ArgoCD across AWS us-east-1 and us-west-2 with automated failover and zero data loss.",
        },
        {
          name: "Infrastructure-as-Code Terraform Module Library",
          description: "Created standardized reusable Terraform modules provisioning SOC2-compliant VPC, EKS, RDS, and IAM policies adopted by 12 internal teams.",
        },
      ],
      certifications: [
        "Certified Kubernetes Administrator (CKA)",
        "AWS Certified DevOps Engineer - Professional",
        "HashiCorp Certified: Terraform Associate",
      ],
    },
    readiness: {
      readiness_score: 91,
      status: "Enterprise Elite Alignment (Exceptional Fit)",
      breakdown: {
        skill_match: 94,
        role_alignment: 92,
        experience_match: 90,
        education_match: 88,
      },
    },
    matched_opportunities: [
      {
        title: "Senior Site Reliability Engineer (SRE)",
        company: "Datadog",
        compatibility_score: 95,
        salary: "$175,000 - $215,000 / yr",
        location: "New York, NY / Remote",
        breakdown: { skill_match: 96, role_alignment: 95, experience_match: 92 },
        why_matched: ["Certified Kubernetes Administrator with verified multi-cluster management", "Advanced Terraform modularization and automated GitOps mastery"],
        gaps: ["eBPF low-level kernel networking", "Chaos engineering drills at hyper-scale"],
      },
      {
        title: "Cloud Infrastructure Architect",
        company: "Snowflake",
        compatibility_score: 90,
        salary: "$165,000 - $205,000 / yr",
        location: "San Mateo, CA / Remote",
        breakdown: { skill_match: 92, role_alignment: 90, experience_match: 88 },
        why_matched: ["Comprehensive AWS Professional credentialing", "Demonstrated SOC2 security compliance automation"],
        gaps: ["Multi-cloud Azure/GCP federation", "Custom Kubernetes Operator development in Go"],
      },
    ],
    learning_plan: [
      {
        course_title: "Kubernetes Operator SDK & Custom Resource Definitions in Go",
        skill: "Cloud Native Extensibility",
        platform: "Cloud Native Computing Foundation (CNCF)",
        priority: "high",
        duration_hours: 20,
        match_confidence: 95,
        relevance_reason: "Essential for building automated platform controllers inside modern EKS/GKE clusters.",
      },
      {
        course_title: "Linux Kernel Observability with eBPF & Cilium",
        skill: "Next-Gen Networking & Security",
        platform: "Isovalent Academy",
        priority: "medium",
        duration_hours: 15,
        match_confidence: 90,
        relevance_reason: "Replaces traditional kube-proxy with lightning-fast kernel-level service routing.",
      },
    ],
    skill_gaps: [
      { skill: "Kubernetes Operators in Go", current_level: 45, required_level: 80, priority: "high", category: "Cloud Systems" },
      { skill: "eBPF Networking with Cilium", current_level: 38, required_level: 75, priority: "medium", category: "Kernel Observability" },
    ],
    industry_intelligence: {
      market_demand: "Critical Demand (Severe Industry Shortage)",
      yoy_growth: "+24.8% YoY",
      avg_salary: "$178,000 / yr (US SRE Average)",
      top_skills_trending: ["Kubernetes", "Terraform", "ArgoCD", "Cilium / eBPF", "AWS", "Go"],
      key_takeaway: "Enterprise platforms are actively upgrading from manual DevOps scripts to automated GitOps and self-healing Kubernetes Operators.",
    },
    agent_summaries: {
      career_readiness: "Outstanding candidate profile with CKA and AWS Professional certifications. Scored 91% readiness with clear leadership-level technical capabilities.",
      skill_analysis: "Core infrastructure, Terraform, and Kubernetes competencies are top-tier. Growth opportunity lies in custom operator development in Golang.",
      learning: "Targeted curriculum covers Go operator controllers and eBPF networking to maximize candidacy for Principal SRE positions.",
      opportunity: "Strong competitive candidacy for positions at Datadog and Snowflake with high salary brackets.",
      industry_intelligence: "SRE profiles with certified Kubernetes engineering remain among the hardest-to-fill tech jobs globally.",
      profile_intelligence: "Exceptional quantification of uptime reliability and blast-radius mitigation across all project bullet points.",
    },
  },

  // 4. Data Scientist & Analytics Engineer
  {
    id: "data-scientist",
    roleName: "Data Scientist",
    category: "AI & Data Science",
    matchPercent: 76,
    candidate: {
      name: "Elena Rostova",
      email: "elena.rostova@skillbridge.ai",
      current_role: "Data Analyst / Junior Scientist",
      location: "Chicago, IL (Open to Relocation)",
      experience_years: 2.0,
      education: [
        "M.S. in Applied Statistics, University of Illinois",
        "B.S. in Economics & Data Analytics",
      ],
      skills: [
        { name: "Python" },
        { name: "R" },
        { name: "SQL (Advanced)" },
        { name: "Pandas & NumPy" },
        { name: "Statsmodels" },
        { name: "Tableau" },
        { name: "A/B Testing Methodology" },
        { name: "Scikit-Learn" },
        { name: "dbt (data build tool)" },
        { name: "Snowflake" },
      ],
      projects: [
        {
          name: "Customer Retention & Churn Predictive Modeling",
          description: "Developed XGBoost churn survival models delivering 87% AUC-ROC, allowing marketing to proactively retain $1.2M in annual recurring revenue.",
        },
        {
          name: "Enterprise Experimentation & A/B Testing Suite",
          description: "Engineered automated statistical significance testing pipeline accounting for network effects and sample ratio mismatches.",
        },
      ],
      certifications: [
        "dbt Certified Developer",
        "Tableau Desktop Specialist",
      ],
    },
    readiness: {
      readiness_score: 76,
      status: "Solid Alignment (Strong Statistical Core)",
      breakdown: {
        skill_match: 78,
        role_alignment: 80,
        experience_match: 72,
        education_match: 86,
      },
    },
    matched_opportunities: [
      {
        title: "Data Scientist - Product Experimentation",
        company: "Uber",
        compatibility_score: 84,
        salary: "$145,000 - $185,000 / yr",
        location: "San Francisco, CA / Hybrid",
        breakdown: { skill_match: 86, role_alignment: 85, experience_match: 78 },
        why_matched: ["Rigorous statistical hypothesis testing foundation", "Proven churn predictive modeling experience"],
        gaps: ["Causal inference and synthetic controls", "PySpark large-scale distributed computing"],
      },
      {
        title: "Analytics Engineer / Data Scientist",
        company: "Spotify",
        compatibility_score: 81,
        salary: "$140,000 - $180,000 / yr",
        location: "New York, NY / Remote",
        breakdown: { skill_match: 84, role_alignment: 82, experience_match: 76 },
        why_matched: ["Certified dbt data modeling expertise on Snowflake", "Advanced SQL aggregation and dimensional modeling"],
        gaps: ["Real-time streaming analytics with Flink", "Deep learning sequence modeling for user journey"],
      },
    ],
    learning_plan: [
      {
        course_title: "Causal Inference and Quasi-Experiments for Tech Companies",
        skill: "Advanced Causal Inference",
        platform: "HarvardX",
        priority: "high",
        duration_hours: 24,
        match_confidence: 92,
        relevance_reason: "Crucial for answering counterfactual business questions when A/B testing is unfeasible.",
      },
      {
        course_title: "Big Data Processing with PySpark & Databricks",
        skill: "Distributed Data Engineering",
        platform: "Coursera",
        priority: "high",
        duration_hours: 20,
        match_confidence: 88,
        relevance_reason: "Scales pandas workflows to multi-terabyte enterprise data lakes.",
      },
    ],
    skill_gaps: [
      { skill: "Causal Inference (Difference-in-Differences / Synthetic Controls)", current_level: 42, required_level: 82, priority: "high", category: "Statistics" },
      { skill: "Apache Spark / PySpark at Scale", current_level: 38, required_level: 78, priority: "high", category: "Big Data" },
      { skill: "Airflow Pipeline Orchestration", current_level: 50, required_level: 75, priority: "medium", category: "Data Pipelines" },
    ],
    industry_intelligence: {
      market_demand: "High & Evolving toward Analytics Engineering",
      yoy_growth: "+21.3% YoY",
      avg_salary: "$152,000 / yr (Industry Average)",
      top_skills_trending: ["Python", "SQL", "dbt", "Snowflake", "Causal Inference", "PySpark"],
      key_takeaway: "The boundary between Data Science and Analytics Engineering is blurring; companies highly value candidates proficient in dbt, data modeling, and rigorous causal statistics.",
    },
    agent_summaries: {
      career_readiness: "Candidate features an outstanding statistical grounding from UIUC master's program. Scored at 76% readiness with straightforward roadmap to cross 85%+.",
      skill_analysis: "SQL and statistical testing proficiencies are excellent. Growth opportunities lie in scaling code via PySpark and mastering causal inference techniques.",
      learning: "Prioritized PySpark and Causal Inference courses will immediately position candidate for top product analytics interviews.",
      opportunity: "Uber and Spotify matches showcase strong alignment with product experimentation and data platform teams.",
      industry_intelligence: "Companies are paying top dollar for data professionals who bridge raw data modeling (dbt) with executive decision science.",
      profile_intelligence: "Resume highlights business impact ($1.2M retained ARR) effectively; suggest adding sample sizes and p-values to experimentation metrics.",
    },
  },

  // 5. Cybersecurity & AppSec Analyst
  {
    id: "cybersecurity",
    roleName: "Cybersecurity Analyst",
    category: "Security & Governance",
    matchPercent: 85,
    candidate: {
      name: "Devon Patel",
      email: "devon.patel@skillbridge.ai",
      current_role: "Information Security Associate",
      location: "Washington, DC (Open to Remote)",
      experience_years: 3.0,
      education: [
        "B.S. in Cybersecurity & Information Assurance, Purdue University",
      ],
      skills: [
        { name: "SIEM (Splunk / Microsoft Sentinel)" },
        { name: "Network Security & Wireshark" },
        { name: "Vulnerability Scanning (Nessus)" },
        { name: "Python / Bash Scripting" },
        { name: "SOC Operations" },
        { name: "OWASP Top 10" },
        { name: "Incident Response" },
        { name: "IAM & Zero Trust Concepts" },
        { name: "Linux Security Hardening" },
        { name: "MITRE ATT&CK Framework" },
      ],
      projects: [
        {
          name: "Automated Incident Triage Playbook in Sentinel",
          description: "Engineered SOAR playbooks that cut Mean Time to Respond (MTTR) by 43% for phishing and credential-stuffing alerts across 8,000 endpoints.",
        },
        {
          name: "Web Application Penetration Test & Threat Modeling",
          description: "Performed rigorous red-team security audits pinpointing 4 critical IDOR and SSRF vulnerabilities before enterprise customer rollout.",
        },
      ],
      certifications: [
        "CompTIA Security+",
        "Certified Information Systems Security Professional (CISSP Associate)",
        "Certified Ethical Hacker (CEH)",
      ],
    },
    readiness: {
      readiness_score: 85,
      status: "Strong Candidate (Security Posture High)",
      breakdown: {
        skill_match: 88,
        role_alignment: 86,
        experience_match: 82,
        education_match: 89,
      },
    },
    matched_opportunities: [
      {
        title: "Cyber Threat Intelligence & Incident Responder",
        company: "CrowdStrike",
        compatibility_score: 91,
        salary: "$150,000 - $190,000 / yr",
        location: "Sunnyvale, CA / Remote",
        breakdown: { skill_match: 92, role_alignment: 90, experience_match: 85 },
        why_matched: ["MITRE ATT&CK framework tactical correlation expertise", "Demonstrated SOAR automated playbook development"],
        gaps: ["Advanced malware reverse engineering (Ghidra)", "Memory forensics in Linux environments"],
      },
      {
        title: "Application Security (AppSec) Engineer",
        company: "Palo Alto Networks",
        compatibility_score: 86,
        salary: "$145,000 - $185,000 / yr",
        location: "Reston, VA / Hybrid",
        breakdown: { skill_match: 88, role_alignment: 86, experience_match: 81 },
        why_matched: ["Hands-on OWASP Top 10 web exploitation testing", "Security hardening across hybrid enterprise environments"],
        gaps: ["Static and Dynamic SAST/DAST CI/CD integration", "Kubernetes runtime threat detection (Falco)"],
      },
    ],
    learning_plan: [
      {
        course_title: "Cloud Native AppSec: Integrating SAST/DAST into DevSecOps",
        skill: "DevSecOps Automation",
        platform: "SANS Institute",
        priority: "high",
        duration_hours: 22,
        match_confidence: 94,
        relevance_reason: "Transforms reactive SOC monitoring into proactive shift-left code scanning.",
      },
    ],
    skill_gaps: [
      { skill: "DevSecOps Pipeline Security (Semgrep / Snyk)", current_level: 45, required_level: 82, priority: "high", category: "Application Security" },
      { skill: "Malware Reverse Engineering & Assembly", current_level: 30, required_level: 70, priority: "medium", category: "Forensics" },
    ],
    industry_intelligence: {
      market_demand: "Extremely High (Zero-Unemployment Domain)",
      yoy_growth: "+31.5% YoY",
      avg_salary: "$158,000 / yr (Enterprise Security Baseline)",
      top_skills_trending: ["SIEM / SOAR", "Zero Trust", "DevSecOps", "Cloud Security", "MITRE ATT&CK"],
      key_takeaway: "Enterprise compliance mandates and ransomware risks have created sustained, recession-proof demand for security engineers with automation skills.",
    },
    agent_summaries: {
      career_readiness: "Candidate features certified Security+ and CISSP Associate standing with verified incident response automation metrics. 85% readiness calibrated.",
      skill_analysis: "SOC triage, log correlation, and MITRE mapping are top percentile. Strategic upside lies in automating SAST/DAST scans in developer CI pipelines.",
      learning: "DevSecOps training roadmap will expand candidate into high-paying application security roles.",
      opportunity: "CrowdStrike and Palo Alto Networks offer direct matches with candidate's threat mitigation background.",
      industry_intelligence: "Cybersecurity remains one of the fastest growing tech specialties with high salary elasticity.",
      profile_intelligence: "High credibility with concrete metrics (43% MTTR reduction) and recognized industry certifications.",
    },
  },

  // 6. Backend Systems Architect (Go & Distributed Systems)
  {
    id: "backend-architect",
    roleName: "Backend Systems Architect",
    category: "Infrastructure & Platform Engineering",
    matchPercent: 79,
    candidate: {
      name: "Sophia Lin",
      email: "sophia.lin@skillbridge.ai",
      current_role: "Senior Backend Engineer",
      location: "Seattle, WA (Remote Friendly)",
      experience_years: 4.5,
      education: [
        "B.S. in Computer Science, University of Washington",
      ],
      skills: [
        { name: "Go (Golang)" },
        { name: "Python" },
        { name: "gRPC & Protocol Buffers" },
        { name: "PostgreSQL & Database Internals" },
        { name: "Redis" },
        { name: "Distributed Systems Concepts" },
        { name: "Docker" },
        { name: "Linux Performance Profiling (pprof)" },
        { name: "Raft Consensus Protocol" },
        { name: "Concurrency & Goroutines" },
      ],
      projects: [
        {
          name: "High-Throughput Distributed Key-Value Store",
          description: "Implemented Raft consensus algorithm in Go with WAL persistence, achieving 80,000 writes/sec with automated leader election.",
        },
        {
          name: "Microservices Service Mesh Gateway",
          description: "Engineered ultra-low latency gRPC proxy reducing inter-service serialization overhead by 62% compared to REST/JSON.",
        },
      ],
      certifications: [
        "Confluent Certified Developer for Apache Kafka",
      ],
    },
    readiness: {
      readiness_score: 79,
      status: "Advanced Competence (Deep Systems Understanding)",
      breakdown: {
        skill_match: 83,
        role_alignment: 80,
        experience_match: 76,
        education_match: 85,
      },
    },
    matched_opportunities: [
      {
        title: "Distributed Systems Engineer (Go)",
        company: "Cloudflare",
        compatibility_score: 87,
        salary: "$170,000 - $215,000 / yr",
        location: "Seattle, WA / Remote",
        breakdown: { skill_match: 88, role_alignment: 86, experience_match: 82 },
        why_matched: ["Deep Go concurrency and pprof memory profiling mastery", "Proven Raft distributed consensus implementation"],
        gaps: ["BGP routing and Anycast edge network protocols", "eBPF low-latency packet inspection"],
      },
      {
        title: "Core Infrastructure Backend Architect",
        company: "Coinbase",
        compatibility_score: 82,
        salary: "$180,000 - $230,000 / yr",
        location: "Remote",
        breakdown: { skill_match: 84, role_alignment: 82, experience_match: 78 },
        why_matched: ["High-throughput gRPC and deterministic WAL logging experience", "Strict database transaction isolation expertise"],
        gaps: ["Hardware Security Modules (HSM) key management", "Zero-downtime ledger migration at petabyte scale"],
      },
    ],
    learning_plan: [
      {
        course_title: "Designing Data-Intensive Applications: Distributed Storage",
        skill: "Distributed Storage Internals",
        platform: "MIT OpenCourseWare (6.824)",
        priority: "high",
        duration_hours: 28,
        match_confidence: 96,
        relevance_reason: "Industry gold standard for mastering distributed transactions, linearizability, and Paxos/Raft subtleties.",
      },
    ],
    skill_gaps: [
      { skill: "LSM-Tree Storage Engines & RocksDB Internals", current_level: 42, required_level: 80, priority: "high", category: "Storage Systems" },
      { skill: "Distributed Transaction Coordination (2PC / Sagas)", current_level: 50, required_level: 85, priority: "high", category: "Architecture" },
    ],
    industry_intelligence: {
      market_demand: "Very High in Fintech, Cloud & Crypto",
      yoy_growth: "+22.4% YoY",
      avg_salary: "$185,000 / yr (Senior Backend Average)",
      top_skills_trending: ["Go", "gRPC", "Raft / Consensus", "PostgreSQL", "Kafka", "Redis"],
      key_takeaway: "Companies processing high transaction volumes rely heavily on Go engineers who write clean, zero-allocation concurrent code.",
    },
    agent_summaries: {
      career_readiness: "Exceptional code quality and systems thinking evident in Raft implementation. 79% score reflects high baseline with clear path to principal level.",
      skill_analysis: "Golang concurrency and network programming are top tier. Growth recommendation is to master LSM-tree storage engines and multi-datacenter replication.",
      learning: "MIT 6.824 curriculum bridges theoretical distributed systems guarantees with production engineering.",
      opportunity: "Prime candidateship for Cloudflare and Coinbase core infrastructure teams.",
      industry_intelligence: "Go backend systems engineers continue to out-earn generalized web developers by 25%+ at Tier-1 companies.",
      profile_intelligence: "Well-documented architecture projects with GitHub links and performance benchmarks.",
    },
  },

  // 7. Technical Product Manager
  {
    id: "tech-pm",
    roleName: "Technical Product Manager",
    category: "Product & Strategy",
    matchPercent: 87,
    candidate: {
      name: "Arjun Mehta",
      email: "arjun.mehta@skillbridge.ai",
      current_role: "Technical Product Manager",
      location: "San Jose, CA (Hybrid / Remote)",
      experience_years: 4.0,
      education: [
        "MBA in Technology Management, Carnegie Mellon University",
        "B.S. in Computer Science",
      ],
      skills: [
        { name: "Product Roadmap Strategy" },
        { name: "Technical PRDs & Spec Writing" },
        { name: "Agile / Scrum Leadership" },
        { name: "API & System Architecture Understanding" },
        { name: "Data Analytics (SQL / Mixpanel)" },
        { name: "User Journey Mapping" },
        { name: "Go-to-Market (GTM) Strategy" },
        { name: "Stakeholder Management" },
        { name: "Competitive Market Analysis" },
        { name: "A/B Testing Frameworks" },
      ],
      projects: [
        {
          name: "Developer API Platform Launch (Zero to 1)",
          description: "Spearheaded technical product lifecycle for enterprise payment gateway APIs, onboarding 200+ partner developers and generating $4.5M in year-one volume.",
        },
        {
          name: "Internal Machine Learning Platform Roadmap",
          description: "Unified disparate ML training tooling into self-service internal developer portal, reducing model deployment cycle time from 3 weeks to 2 days.",
        },
      ],
      certifications: [
        "Certified Scrum Product Owner (CSPO)",
        "Pragmatic Institute Certified (PMC-III)",
      ],
    },
    readiness: {
      readiness_score: 87,
      status: "High Executive Alignment (Senior PM Ready)",
      breakdown: {
        skill_match: 90,
        role_alignment: 88,
        experience_match: 85,
        education_match: 91,
      },
    },
    matched_opportunities: [
      {
        title: "Staff Technical Product Manager - Developer Tools",
        company: "GitHub",
        compatibility_score: 92,
        salary: "$175,000 - $220,000 / yr",
        location: "San Francisco, CA / Remote",
        breakdown: { skill_match: 94, role_alignment: 92, experience_match: 88 },
        why_matched: ["Demonstrated success launching developer-facing API platforms", "CS background enabling high-bandwidth engineering collaboration"],
        gaps: ["AI-assisted developer workflow telemetry", "Enterprise seat expansion pricing tiers"],
      },
      {
        title: "Principal Technical Product Manager",
        company: "Amazon Web Services (AWS)",
        compatibility_score: 86,
        salary: "$180,000 - $235,000 / yr",
        location: "Seattle, WA / Hybrid",
        breakdown: { skill_match: 88, role_alignment: 86, experience_match: 82 },
        why_matched: ["Exceptional backwards-working PR/FAQ writing capability", "Verifiable enterprise revenue outcomes ($4.5M)"],
        gaps: ["Global multi-region cloud service compliance", "Tier-0 service operational readiness reviews"],
      },
    ],
    learning_plan: [
      {
        course_title: "AI Product Management: Bringing Generative AI to Enterprise",
        skill: "AI Product Strategy",
        platform: "Duke University / Coursera",
        priority: "high",
        duration_hours: 18,
        match_confidence: 94,
        relevance_reason: "Equips technical PMs to lead LLM evaluation, safety guardrails, and unit economics.",
      },
    ],
    skill_gaps: [
      { skill: "Generative AI Unit Economics & Token Pricing", current_level: 45, required_level: 80, priority: "high", category: "AI Strategy" },
      { skill: "FinOps Cloud Cost Optimization Models", current_level: 50, required_level: 78, priority: "medium", category: "Finance" },
    ],
    industry_intelligence: {
      market_demand: "Very High for Developer Platform TPMs",
      yoy_growth: "+20.1% YoY",
      avg_salary: "$182,000 / yr (Senior TPM Benchmark)",
      top_skills_trending: ["Developer APIs", "AI Product Roadmap", "SQL", "PRDs", "GTM Strategy"],
      key_takeaway: "The tech industry increasingly favors Technical PMs with Computer Science roots who can debate architecture tradeoffs directly with principal engineers.",
    },
    agent_summaries: {
      career_readiness: "Exceptional blend of Computer Science pedigree and Carnegie Mellon MBA. 87% readiness reflects strong leadership and technical translation competence.",
      skill_analysis: "Technical PRDs, developer API empathy, and SQL querying are in the 90th percentile. Growth focus is on AI token economics.",
      learning: "AI Product Management course bridges developer platforms into enterprise LLM workflows.",
      opportunity: "High affinity match with GitHub and AWS developer tooling divisions.",
      industry_intelligence: "Technical PMs with hands-on software development experience command the highest compensation multipliers in product management.",
      profile_intelligence: "Outstanding presentation of commercial metrics ($4.5M volume, 3 weeks to 2 days cycle time).",
    },
  },

  // 8. Mobile Applications Developer (Flutter & React Native)
  {
    id: "mobile-dev",
    roleName: "Mobile Applications Developer",
    category: "Mobile & Client Engineering",
    matchPercent: 74,
    candidate: {
      name: "Hannah Kim",
      email: "hannah.kim@skillbridge.ai",
      current_role: "Mobile Software Engineer",
      location: "Toronto, Canada (Open to Remote)",
      experience_years: 2.5,
      education: [
        "B.S. in Software Engineering, University of Waterloo",
      ],
      skills: [
        { name: "Flutter & Dart" },
        { name: "React Native" },
        { name: "TypeScript" },
        { name: "iOS / Swift Basics" },
        { name: "Android / Kotlin Basics" },
        { name: "Mobile CI/CD (Fastlane)" },
        { name: "State Management (Bloc / Redux)" },
        { name: "REST & GraphQL Client Architecture" },
        { name: "Offline-First SQLite / Realm" },
        { name: "App Store & Play Store Release Management" },
      ],
      projects: [
        {
          name: "Cross-Platform Health & Fitness Tracker App",
          description: "Engineered 60fps cross-platform Flutter application with offline SQLite synchronization and Apple HealthKit integration with 150k active downloads.",
        },
        {
          name: "React Native E-Commerce Checkout Flow",
          description: "Re-architected checkout funnel using React Native and native TurboModules, slashing crash rates to 0.04% and increasing completed orders by 14%.",
        },
      ],
      certifications: [
        "Meta Certified React Native Specialist",
      ],
    },
    readiness: {
      readiness_score: 74,
      status: "Solid Alignment (High Client Performance)",
      breakdown: {
        skill_match: 78,
        role_alignment: 76,
        experience_match: 70,
        education_match: 82,
      },
    },
    matched_opportunities: [
      {
        title: "Mobile Engineer (React Native / iOS)",
        company: "Shopify",
        compatibility_score: 83,
        salary: "$135,000 - $175,000 CAD",
        location: "Toronto, ON / Remote",
        breakdown: { skill_match: 85, role_alignment: 82, experience_match: 76 },
        why_matched: ["High-performance React Native TurboModules background", "Fastlane automated App Store release pipelines"],
        gaps: ["Deep Objective-C++ Bridgeless architecture", "Large-scale monorepo mobile tooling"],
      },
      {
        title: "Senior Cross-Platform Mobile Developer",
        company: "Duolingo",
        compatibility_score: 79,
        salary: "$140,000 - $180,000 USD",
        location: "Pittsburgh, PA / Remote",
        breakdown: { skill_match: 82, role_alignment: 78, experience_match: 72 },
        why_matched: ["Smooth 60fps Flutter animation and sound synthesis handling", "Demonstrated offline-first sync architecture"],
        gaps: ["Native Android NDK performance profiling", "Localized multi-language dynamic asset bundles"],
      },
    ],
    learning_plan: [
      {
        course_title: "React Native New Architecture & Turbo Native Modules",
        skill: "Native Mobile Bridge",
        platform: "Frontend Masters",
        priority: "high",
        duration_hours: 16,
        match_confidence: 93,
        relevance_reason: "Crucial for writing direct C++ JSI bindings without JavaScript bridge overhead.",
      },
    ],
    skill_gaps: [
      { skill: "React Native JSI & C++ TurboModules", current_level: 40, required_level: 78, priority: "high", category: "Native Systems" },
      { skill: "Native Android Profiling & ProGuard Hardening", current_level: 45, required_level: 75, priority: "medium", category: "Android" },
    ],
    industry_intelligence: {
      market_demand: "Steady Demand for Cross-Platform Specialists",
      yoy_growth: "+16.2% YoY",
      avg_salary: "$142,000 / yr (Mobile Engineering Average)",
      top_skills_trending: ["React Native", "Flutter", "Swift", "Kotlin", "Fastlane", "JSI"],
      key_takeaway: "Companies are consolidating separate iOS and Android teams into unified cross-platform teams using React Native or Flutter backed by native C++ TurboModules.",
    },
    agent_summaries: {
      career_readiness: "Demonstrated production app deployments on both App Store and Google Play. 74% readiness with rapid path to senior through native bridge mastery.",
      skill_analysis: "Flutter and React Native UI development are excellent. Strategic growth vector is native C++ JSI bindings to remove bridge latency.",
      learning: "Focus on React Native New Architecture and TurboModules will unlock senior roles at Shopify and Duolingo.",
      opportunity: "Solid fit for cross-platform e-commerce and consumer mobile applications.",
      industry_intelligence: "Cross-platform mobile developers who understand native iOS/Android internals command high demand.",
      profile_intelligence: "Excellent real-world user metrics (150k downloads, 0.04% crash rate) stand out on resume review.",
    },
  },
];
