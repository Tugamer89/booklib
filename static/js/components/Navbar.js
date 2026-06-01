import { useTheme } from "../utils/theme.js";
import { BookMarked, Sun, Moon } from "lucide-vue-next";

export default {
    props: ["isAdmin", "username"],
    emits: ["toggle-theme"],
    components: { BookMarked, Sun, Moon },
    setup(props, { emit }) {
        const { toggleTheme, isDark } = useTheme();
        return { toggleTheme, isDark };
    },
    template: `
      <nav class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-lg shadow-sm sticky top-0 z-40">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex items-center justify-between h-16">
            <div class="flex-shrink-0 flex items-center gap-2">
              <BookMarked class="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
              <h1 class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">BookLib</h1>
            </div>
            <div class="flex items-center space-x-4">
              <a v-if="isAdmin" href="/admin/users" class="text-sm font-medium text-slate-600 hover:text-indigo-600 dark:text-slate-300 dark:hover:text-indigo-400 transition rounded focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500">
                Admin
              </a>
              <button @click="toggleTheme" class="p-2 rounded-full text-slate-500 hover:bg-slate-200 dark:text-slate-400 dark:hover:bg-slate-700 transition focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500" aria-label="Toggle theme">
                <Sun v-if="isDark" class="w-5 h-5 text-yellow-500" />
                <Moon v-else class="w-5 h-5 text-slate-500" />
              </button>
              <a href="/logout" class="text-sm font-medium text-slate-600 hover:text-indigo-600 dark:text-slate-300 dark:hover:text-indigo-400 transition rounded focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500">
                Logout
              </a>
            </div>
          </div>
        </div>
      </nav>
    `,
};
