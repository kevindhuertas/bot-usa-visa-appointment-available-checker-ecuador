import type { NextPage } from 'next';
import { GetStaticProps } from 'next';
import Head from 'next/head';
import { serverSideTranslations } from 'next-i18next/serverSideTranslations';
import PageWrapper from '../../../layout/PageWrapper/PageWrapper';
import { pageLayoutTypesPagesMenu } from '../../../menu';
import Humans from '../../../assets/img/scene8.png';
import Page from '../../../layout/Page/Page';
import Popovers from '../../../components/bootstrap/Popovers';

const Index: NextPage = () => {
	return (
		<PageWrapper>
			<Head>
				<title>{pageLayoutTypesPagesMenu.blank.text}</title>
			</Head>
			<Page>
				<div className='row d-flex align-items-center h-100'>
					<div
						className='col-12 d-flex justify-content-center align-items-center'
						style={{ fontSize: 'calc(3rem + 3vw)' }}>
						<Popovers
							title='index.tsx'
							desc={<code>pages/page-layouts/blank/index.tsx</code>}>
							Page
						</Popovers>
						<code className='ps-3'>index.tsx</code>
					</div>
				</div>
			</Page>
		</PageWrapper>
	);
};

export const getStaticProps: GetStaticProps = async ({ locale }) => ({
	props: {
		// @ts-ignore
		...(await serverSideTranslations(locale, ['common', 'menu'])),
	},
});

export default Index;
