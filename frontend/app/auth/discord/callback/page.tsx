'use client';

import { Suspense, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export const dynamic = 'force-dynamic';

function DiscordCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const token = searchParams.get('token');
    const userId = searchParams.get('user_id');
    const nick = searchParams.get('nick');
    const discordName = searchParams.get('discord_name');

    if (token && userId && nick) {
      window.localStorage.setItem(
        'zvz_auth',
        JSON.stringify({
          token,
          userId: Number(userId),
          nick,
          discordName: discordName || nick,
        }),
      );
      router.replace('/participar');
      return;
    }

    router.replace('/?auth=discord_error');
  }, [router, searchParams]);

  return (
    <main className="grid min-h-screen place-items-center px-4 text-zinc-100">
      <section className="surface max-w-md rounded-md p-5 text-center">
        <h1 className="text-lg font-bold text-white">Conectando Discord</h1>
        <p className="mt-2 text-sm text-zinc-400">Finalizando autenticacao e abrindo o check-in.</p>
      </section>
    </main>
  );
}

export default function DiscordCallbackPage() {
  return (
    <Suspense fallback={(
      <main className="grid min-h-screen place-items-center px-4 text-zinc-100">
        <section className="surface max-w-md rounded-md p-5 text-center">
          <h1 className="text-lg font-bold text-white">Conectando Discord</h1>
          <p className="mt-2 text-sm text-zinc-400">Preparando autenticacao.</p>
        </section>
      </main>
    )}>
      <DiscordCallbackContent />
    </Suspense>
  );
}
