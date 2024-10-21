<script lang="ts">
import UserState from './UserState.vue';
import SignOutButton from './SignOutButton.vue';

export default {
  components: { UserState, SignOutButton },
};
</script>

<template>
  <nav class="border-gray-200 bg-gray-800">
    <div class="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
      <RouterLink to="/" class="flex items-center">
        <svg
          class="mx-2"
          height="40"
          viewBox="0 0 64 64"
          width="40"
          xmlns="http://www.w3.org/2000/svg"
          id="fi_5401670"
        >
          <path
            d="m61 25.5a15.00547 15.00547 0 0 1 -15 15h-32a10.82477 10.82477 0 0 1 -2.63-.32 10.99945 10.99945 0 0 1 2.63-21.68 10.53152 10.53152 0 0 1 2.04.2 15.98664 15.98664 0 0 1 15.96-15.2 15.82733 15.82733 0 0 1 9.3 2.99 16.04558 16.04558 0 0 1 3.96 4.05c.24-.01.49-.04.74-.04a15.00543 15.00543 0 0 1 15 15z"
            fill="#4aa5ff"
          ></path>
          <path
            d="m61 25.5a15.00547 15.00547 0 0 1 -15 15h-32a10.82477 10.82477 0 0 1 -2.63-.32 10.997 10.997 0 0 1 8.33-18.18 10.53145 10.53145 0 0 1 2.04.2 15.99342 15.99342 0 0 1 15.96-15.2 15.24366 15.24366 0 0 0 3.6-.51 16.04558 16.04558 0 0 1 3.96 4.05c.24-.01.49-.04.74-.04a15.00543 15.00543 0 0 1 15 15z"
            fill="#e6f3ff"
          ></path>
          <path d="m51 15.70324a11.01224 11.01224 0 0 1 6 9.79676" fill="#e6f3ff"></path>
          <g fill="#4aa5ff">
            <path d="m38 42.5a6 6 0 0 1 -12 0c0-3.31371 6-10 6-10s6 6.68629 6 10z"></path>
            <path d="m24 54.5a6 6 0 0 1 -12 0c0-3.31371 6-10 6-10s6 6.68629 6 10z"></path>
            <path d="m54 48.5a6 6 0 0 1 -12 0c0-3.31371 6-10 6-10s6 6.68629 6 10z"></path>
          </g>
          <path
            d="m46 9.5c-.081 0-.16309.00293-.24414.00684-9.03373-12.47721-28.93347-7.21809-30.625 8.0498a11.99846 11.99846 0 1 0 -1.13086 23.94336h11.13336a6.94692 6.94692 0 1 0 13.73328 0h5.44067c-1.6272 2.24463-3.30731 5.03467-3.30731 7a7 7 0 0 0 14 0c0-2.21515-2.13354-5.47961-3.92072-7.82715 17.03453-5.94336 13.01865-30.86285-5.07928-31.17285zm-14 38a5.00588 5.00588 0 0 1 -5-5c0-1.90625 2.81641-5.88379 5-8.47461 2.18359 2.58984 5 6.56641 5 8.47461a5.00588 5.00588 0 0 1 -5 5zm16 6a5.00588 5.00588 0 0 1 -5-5c-.02981-1.88576 2.96392-6.07648 5-8.47461 2.11345 2.50012 5.01885 6.5864 5 8.47461a5.00587 5.00587 0 0 1 -5 5zm1.73389-14.516c-1.80431-2.38471-2.115-1.6521-3.89118.516h-7.69371a38.78793 38.78793 0 0 0 -5.40485-7.668 1.03326 1.03326 0 0 0 -1.48828 0 38.78793 38.78793 0 0 0 -5.40487 7.668h-11.851a10 10 0 0 1 0-20c.99992-.12126 2.85327.82392 3.03906-.75a14.98891 14.98891 0 0 1 27.39258-7.6494c.3408.56629 1.01648.4246 1.56836.39937 16.23857.31497 19.31439 22.91061 3.73389 27.48403z"
            fill="#21257c"
          ></path>
          <path
            d="m17.25586 43.832c-.64063.7139-6.25586 7.07523-6.25586 10.668.3286 9.26291 13.67163 9.26344 14-.00012 0-3.59265-5.61524-9.954-6.25587-10.66785a1.03326 1.03326 0 0 0 -1.48827-.00003zm.74414 15.668a5.00588 5.00588 0 0 1 -5-5c0-1.90625 2.81641-5.88379 5-8.47461 2.18359 2.58984 5 6.56641 5 8.47461a5.00588 5.00588 0 0 1 -5 5z"
            fill="#21257c"
          ></path>
        </svg>
        <span class="self-center text-2xl font-semibold whitespace-nowrap text-white"
          >Rainfall</span
        >
      </RouterLink>
      <ul
        class="w-full md:w-auto font-medium flex flex-col text-center md:text-left p-4 md:p-0 mt-4 border rounded-lg md:flex-row md:space-x-8 md:mt-0 md:border-0 bg-gray-800 border-gray-700"
      >
        <li>
          <RouterLink
            to="/sites"
            class="block py-2 pl-3 pr-4 text-gray-900 rounded h-8 hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:pt-2 text-white md:hover:text-blue-500 hover:bg-gray-700 hover:text-white md:hover:bg-transparent"
            >Sites</RouterLink
          >
        </li>
        <li>
          <UserState class="user-state py-2 pl-3 pr-4 md:pt-2 text-white" />
        </li>
        <li>
          <SignOutButton class="py-2 pl-3 pr-4 md:p-0 text-white" />
        </li>
      </ul>
    </div>
  </nav>
</template>

<style scoped></style>
