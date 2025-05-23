import Image from 'next/image';
import Link from 'next/link';

interface Ingredient {
  name: string;
  amount: string;
  unit: string;
}

interface RecipeCardProps {
  id: string;
  title: string;
  image_url: string;
  categories: string[];
  calories: number;
  estimated_time_min: number;
}

export default function RecipeCard({
  id,
  title,
  image_url,
  categories,
  calories,
  estimated_time_min,
}: RecipeCardProps) {
  return (
    <Link href={`/recipe/${id}`}>
      <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
        <div className="relative h-48">
          <Image
            src={image_url}
            alt={title}
            fill
            className="object-cover"
          />
        </div>
        <div className="p-4">
          <h3 className="text-lg font-semibold mb-2">{title}</h3>
          <div className="flex flex-wrap gap-2 mb-3">
            {categories.map((category) => (
              <span
                key={category}
                className="px-2 py-1 text-sm bg-gray-100 rounded-full"
              >
                {category}
              </span>
            ))}
          </div>
          <div className="flex justify-between text-sm text-gray-600">
            <span>🕒 {estimated_time_min} мин</span>
            <span>🔥 {calories} ккал</span>
          </div>
        </div>
      </div>
    </Link>
  );
} 