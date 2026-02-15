export const users = [
  { id: 1, username: "Admin", joinDate: "Jan 2020", posts: 1542, role: "Administrator" },
  { id: 2, username: "JohnDoe", joinDate: "Mar 2021", posts: 387, role: "Senior Member" },
  { id: 3, username: "JaneSmith", joinDate: "Jul 2021", posts: 214, role: "Member" },
  { id: 4, username: "TechGuru", joinDate: "Nov 2020", posts: 891, role: "Moderator" },
  { id: 5, username: "NewUser42", joinDate: "Dec 2024", posts: 12, role: "Junior Member" },
];

export const categories = [
  {
    id: 1,
    groupName: "General",
    forums: [
      { id: 1, name: "Announcements", description: "Official announcements and news", threads: 23, posts: 156, lastPost: { author: "Admin", date: "Today, 10:32 AM", thread: "Forum Rules Updated" } },
      { id: 2, name: "Introductions", description: "New here? Say hello!", threads: 89, posts: 412, lastPost: { author: "NewUser42", date: "Today, 09:15 AM", thread: "Hi everyone!" } },
    ],
  },
  {
    id: 2,
    groupName: "Technology",
    forums: [
      { id: 3, name: "Programming", description: "Discuss programming languages, frameworks, and tools", threads: 234, posts: 1893, lastPost: { author: "TechGuru", date: "Today, 11:45 AM", thread: "Best practices for REST APIs" } },
      { id: 4, name: "Hardware", description: "CPUs, GPUs, builds, and peripherals", threads: 156, posts: 987, lastPost: { author: "JohnDoe", date: "Yesterday, 08:22 PM", thread: "New GPU benchmark results" } },
      { id: 5, name: "Networking", description: "Routers, switches, protocols, and home labs", threads: 67, posts: 345, lastPost: { author: "JaneSmith", date: "Yesterday, 03:10 PM", thread: "Setting up VLANs" } },
    ],
  },
  {
    id: 3,
    groupName: "Off-Topic",
    forums: [
      { id: 6, name: "Lounge", description: "Chat about anything and everything", threads: 312, posts: 2456, lastPost: { author: "JohnDoe", date: "Today, 12:01 PM", thread: "What are you listening to?" } },
      { id: 7, name: "Gaming", description: "Video games, board games, and more", threads: 178, posts: 1234, lastPost: { author: "JaneSmith", date: "Today, 08:50 AM", thread: "Favorite games of 2025" } },
    ],
  },
];

export const threads = {
  1: [
    { id: 1, title: "Forum Rules Updated", authorId: 1, replies: 5, views: 234, lastPost: { author: "JohnDoe", date: "Today, 10:32 AM" }, sticky: true },
    { id: 2, title: "Welcome to the new forum!", authorId: 1, replies: 12, views: 567, lastPost: { author: "JaneSmith", date: "Yesterday, 04:20 PM" }, sticky: true },
    { id: 3, title: "Scheduled maintenance this weekend", authorId: 1, replies: 3, views: 89, lastPost: { author: "NewUser42", date: "Yesterday, 11:00 AM" }, sticky: false },
  ],
  2: [
    { id: 4, title: "Hi everyone!", authorId: 5, replies: 4, views: 45, lastPost: { author: "Admin", date: "Today, 09:30 AM" }, sticky: false },
    { id: 5, title: "Long time lurker, first post", authorId: 3, replies: 8, views: 102, lastPost: { author: "JohnDoe", date: "Yesterday, 06:00 PM" }, sticky: false },
  ],
  3: [
    { id: 6, title: "Best practices for REST APIs", authorId: 4, replies: 15, views: 432, lastPost: { author: "JaneSmith", date: "Today, 11:45 AM" }, sticky: false },
    { id: 7, title: "Python vs Go for backend?", authorId: 2, replies: 28, views: 891, lastPost: { author: "TechGuru", date: "Today, 10:00 AM" }, sticky: false },
    { id: 8, title: "Help with async/await", authorId: 5, replies: 6, views: 178, lastPost: { author: "Admin", date: "Yesterday, 09:15 PM" }, sticky: false },
    { id: 9, title: "Git workflow for small teams", authorId: 3, replies: 11, views: 267, lastPost: { author: "JohnDoe", date: "Yesterday, 02:30 PM" }, sticky: false },
    { id: 10, title: "Docker compose tips", authorId: 4, replies: 9, views: 345, lastPost: { author: "NewUser42", date: "2 days ago" }, sticky: false },
  ],
  4: [
    { id: 11, title: "New GPU benchmark results", authorId: 2, replies: 22, views: 654, lastPost: { author: "TechGuru", date: "Yesterday, 08:22 PM" }, sticky: false },
    { id: 12, title: "Best budget keyboard 2025?", authorId: 5, replies: 14, views: 321, lastPost: { author: "JaneSmith", date: "2 days ago" }, sticky: false },
  ],
  5: [
    { id: 13, title: "Setting up VLANs", authorId: 3, replies: 7, views: 189, lastPost: { author: "TechGuru", date: "Yesterday, 03:10 PM" }, sticky: false },
  ],
  6: [
    { id: 14, title: "What are you listening to?", authorId: 2, replies: 45, views: 890, lastPost: { author: "JaneSmith", date: "Today, 12:01 PM" }, sticky: false },
    { id: 15, title: "Coffee or tea?", authorId: 3, replies: 67, views: 1200, lastPost: { author: "NewUser42", date: "Today, 07:30 AM" }, sticky: false },
  ],
  7: [
    { id: 16, title: "Favorite games of 2025", authorId: 3, replies: 19, views: 445, lastPost: { author: "TechGuru", date: "Today, 08:50 AM" }, sticky: false },
  ],
};

export const posts = {
  6: [
    {
      id: 1,
      authorId: 4,
      date: "Yesterday, 08:00 AM",
      content: "I've been working with REST APIs for years and wanted to share some best practices I've picked up along the way.\n\n1. Use nouns for endpoints, not verbs\n2. Use proper HTTP status codes\n3. Version your API\n4. Implement pagination for list endpoints\n5. Use consistent error response formats\n\nWhat would you add to this list?",
    },
    {
      id: 2,
      authorId: 2,
      date: "Yesterday, 09:30 AM",
      content: "Great list! I'd add:\n\n6. Use HATEOAS where appropriate\n7. Always validate input on the server side\n8. Rate limiting is a must for public APIs\n\nAlso, documentation is huge. I use OpenAPI/Swagger for all my projects now.",
    },
    {
      id: 3,
      authorId: 3,
      date: "Yesterday, 02:15 PM",
      content: "Don't forget about authentication and authorization! JWT tokens are popular but make sure you understand the tradeoffs vs session-based auth.\n\nAlso +1 on the documentation point. FastAPI generates it automatically which is awesome.",
    },
    {
      id: 4,
      authorId: 1,
      date: "Today, 11:45 AM",
      content: "All excellent points. I'd also recommend:\n\n- Use consistent naming conventions (camelCase vs snake_case — pick one and stick with it)\n- Implement proper CORS handling\n- Log everything, but sanitize sensitive data from logs\n\nWe actually follow most of these on this forum's backend!",
    },
  ],
  7: [
    {
      id: 5,
      authorId: 2,
      date: "3 days ago",
      content: "I've been debating whether to use Python or Go for my next backend project. Python has great libraries and FastAPI is amazing, but Go has incredible performance and concurrency support.\n\nWhat are your thoughts? What do you prefer and why?",
    },
    {
      id: 6,
      authorId: 4,
      date: "3 days ago",
      content: "It really depends on the use case:\n\n- Python/FastAPI: Great for rapid development, data-heavy apps, ML integration\n- Go: Better for high-concurrency services, microservices, CLI tools\n\nI use both depending on the project. For a typical web API, I'd go with Python for the faster development cycle.",
    },
    {
      id: 7,
      authorId: 5,
      date: "2 days ago",
      content: "I'm still learning both but Python feels way more beginner-friendly. The ecosystem is huge and there's a tutorial for everything.",
    },
  ],
};

export function getUserById(id) {
  return users.find((u) => u.id === id);
}

export function getCategoryForums() {
  return categories;
}

export function getForumById(forumId) {
  for (const cat of categories) {
    const forum = cat.forums.find((f) => f.id === forumId);
    if (forum) return { ...forum, groupName: cat.groupName };
  }
  return null;
}

export function getThreadsByForumId(forumId) {
  return threads[forumId] || [];
}

export function getThreadById(threadId) {
  for (const forumThreads of Object.values(threads)) {
    const thread = forumThreads.find((t) => t.id === threadId);
    if (thread) return thread;
  }
  return null;
}

export function getForumIdByThreadId(threadId) {
  for (const [forumId, forumThreads] of Object.entries(threads)) {
    if (forumThreads.find((t) => t.id === threadId)) return Number(forumId);
  }
  return null;
}

export function getPostsByThreadId(threadId) {
  return posts[threadId] || [];
}
