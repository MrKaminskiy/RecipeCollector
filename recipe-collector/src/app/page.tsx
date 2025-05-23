'use client';

import { useState } from 'react';
import LinkInput from '@/components/LinkInput';
import RecipeCard from '@/components/RecipeCard';
import Navbar from '@/components/Navbar';

interface Recipe {
  id: string;
  title: string;
  image_url: string;
  categories: string[];
  calories: number;
  estimated_time_min: number;
}

export default function HomePage() {
  const [isLoading, setIsLoading] = useState(false);
  const [recipes, setRecipes] = useState<Recipe[]>([]);

  const handleSubmit = async (url: string) => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/parse', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error('Ошибка при обработке рецепта');
      }

      const recipe = await response.json();
      setRecipes((prev) => [recipe, ...prev]);
    } catch (error) {
      console.error('Error:', error);
      // TODO: Добавить обработку ошибок
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              Соберите свои любимые рецепты
            </h1>
            <p className="text-gray-600 mb-8">
              Вставьте ссылку на рецепт из Instagram, TikTok или веб-страницы, и мы автоматически создадим структурированную карточку рецепта.
            </p>
            <LinkInput onSubmit={handleSubmit} isLoading={isLoading} />
          </div>

          <div className="mt-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Ваши рецепты
            </h2>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {recipes.map((recipe) => (
                <RecipeCard key={recipe.id} {...recipe} />
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
