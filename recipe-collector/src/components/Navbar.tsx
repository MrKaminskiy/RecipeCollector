import Link from 'next/link';
import { useRouter } from 'next/router';

export default function Navbar() {
  const router = useRouter();
  const isAuthenticated = false; // TODO: Заменить на реальную проверку авторизации

  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center">
              <span className="text-xl font-bold text-blue-600">Recipe Collector</span>
            </Link>
          </div>

          <div className="flex items-center">
            {isAuthenticated ? (
              <button
                onClick={() => {/* TODO: Реализовать выход */}}
                className="ml-4 px-4 py-2 text-sm text-gray-700 hover:text-gray-900"
              >
                Выйти
              </button>
            ) : (
              <Link
                href="/login"
                className="ml-4 px-4 py-2 text-sm text-white bg-blue-600 rounded-md hover:bg-blue-700"
              >
                Войти
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
} 